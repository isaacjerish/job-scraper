# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os
from upstash_redis import Redis
import time

# Import the JSearch scraper
from scrapers.jsearch_scraper import scrape_jsearch

# Import our helper functions
from api.filter import filter_jobs
from api.notify import send_to_discord

# --- Get API Keys and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")

# --- Instantiate the Upstash Redis client ---
KV_URL = os.environ.get("KV_REST_API_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")

redis = None
if KV_URL and KV_TOKEN:
    redis = Redis(url=KV_URL, token=KV_TOKEN)
else:
    print("KV database credentials not found. De-duplication will be disabled.")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not JSEARCH_API_KEY:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"JSearch API Key not found.")
            return

        # 1. Scrape for jobs
        all_jobs = scrape_jsearch(JSEARCH_API_KEY)

        # 2. Manually filter for jobs posted in the last 3 days
        three_days_ago_timestamp = int(time.time()) - (3 * 24 * 60 * 60)
        recent_jobs = []
        for job in all_jobs:
            if job.get("posted_at") and job["posted_at"] > three_days_ago_timestamp:
                recent_jobs.append(job)

        # 3. Filter out jobs we've already seen
        new_unseen_jobs = []
        if redis:
            for job in recent_jobs:
                job_url = job.get("url")
                if job_url and not redis.exists(job_url):
                    new_unseen_jobs.append(job)
        else:
            new_unseen_jobs = recent_jobs

        # 4. Apply our custom quality filter
        final_filtered_jobs = filter_jobs(new_unseen_jobs)

        # 5. Notify and update the database
        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
            send_to_discord(DISCORD_WEBHOOK_URL, final_filtered_jobs)

            if redis:
                print(
                    f"Adding {len(final_filtered_jobs)} new job URLs to the database..."
                )
                for job in final_filtered_jobs:
                    redis.set(job["url"], "seen", ex=2592000)  # 30-day expiration

        # 6. Respond to the HTTP request
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "success", "found_jobs": len(final_filtered_jobs)}
            ).encode("utf-8")
        )
