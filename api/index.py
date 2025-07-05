# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os
from upstash_redis import Redis  # <-- Import the new Upstash Redis client

# Import the JSearch scraper
from scrapers.jsearch_scraper import scrape_jsearch

# Import our helper functions
from api.filter import filter_jobs
from api.notify import send_to_discord

# --- Get API Keys and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")

# --- Instantiate the Upstash Redis client ---
# It automatically uses the environment variables set by the Vercel integration
redis = Redis.from_env()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # --- 1. Scrape for all recent jobs ---
        if not JSEARCH_API_KEY:
            print("JSearch API Key not found. Cannot perform search.")
            self.send_response(200)
            self.end_headers()
            return

        all_jobs = scrape_jsearch(JSEARCH_API_KEY)

        if not all_jobs:
            print("No jobs found from JSearch. Exiting.")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "success", "found_jobs": 0}).encode("utf-8")
            )
            return

        # --- 2. Filter out jobs we've already seen ---
        new_unseen_jobs = []
        for job in all_jobs:
            job_url = job.get("url")
            if not job_url:
                continue  # Skip jobs without a URL

            # Check if the job URL exists as a key in our Redis store
            # The .exists() method returns the number of keys found (0 or 1)
            if not redis.exists(job_url):
                new_unseen_jobs.append(job)

        print(f"Found {len(new_unseen_jobs)} new, unseen jobs.")

        # --- 3. Apply our custom quality filter ---
        final_filtered_jobs = filter_jobs(new_unseen_jobs)

        print(
            f"Found {len(final_filtered_jobs)} relevant new jobs after final filtering."
        )

        # --- 4. Notify and update the database for new jobs ---
        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
            send_to_discord(DISCORD_WEBHOOK_URL, final_filtered_jobs)

            # Add the new job URLs to the database so we don't see them again
            # We set a TTL (Time To Live) of 30 days on each key to keep the database clean
            print(f"Adding {len(final_filtered_jobs)} new job URLs to the database...")
            for job in final_filtered_jobs:
                # .set() with 'ex' sets the key with an expiration in seconds
                redis.set(job["url"], "seen", ex=2592000)  # 2592000 seconds = 30 days

        # Respond to the HTTP request
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "success", "found_jobs": len(final_filtered_jobs)}
            ).encode("utf-8")
        )
