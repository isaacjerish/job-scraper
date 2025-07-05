# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os
from upstash_redis import Redis  # <-- Import the new Upstash Redis client

# Import the JSearch scraper
from scrapers.jsearch_scraper import scrape_jsearch

# Import our helper functions
from api.filter import filter_jobs

# We now import both notification functions
from api.notify import send_to_discord, send_status_update

# --- Get API Keys and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")

# --- Instantiate the Upstash Redis client ---
# Get the database credentials from the environment variables Vercel created.
KV_URL = os.environ.get("KV_REST_API_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")

# Initialize the redis client variable
redis = None
if KV_URL and KV_TOKEN:
    redis = Redis(url=KV_URL, token=KV_TOKEN)
else:
    print("KV database credentials not found. De-duplication will be disabled.")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # --- 1. Scrape for all recent jobs ---
        if not JSEARCH_API_KEY:
            print("JSearch API Key not found. Cannot perform search.")
            self.send_response(200)
            self.end_headers()
            return

        all_jobs = scrape_jsearch(JSEARCH_API_KEY)
        total_jobs_from_api = len(all_jobs)

        # --- 2. Filter out jobs we've already seen ---
        new_unseen_jobs = []
        if redis:  # Only perform de-duplication if the database is connected
            for job in all_jobs:
                job_url = job.get("url")
                if not job_url:
                    continue  # Skip jobs without a URL

                # Check if the job URL exists as a key in our Redis store
                if not redis.exists(job_url):
                    new_unseen_jobs.append(job)
        else:
            # If DB is not connected, treat all jobs as new
            new_unseen_jobs = all_jobs

        new_unseen_count = len(new_unseen_jobs)
        print(f"Found {new_unseen_count} new, unseen jobs.")

        # --- 3. Apply our custom quality filter ---
        final_filtered_jobs = filter_jobs(new_unseen_jobs)
        final_filtered_count = len(final_filtered_jobs)

        print(f"Found {final_filtered_count} relevant new jobs after final filtering.")

        # --- 4. Notify about new jobs (if any) and update database ---
        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
            send_to_discord(DISCORD_WEBHOOK_URL, final_filtered_jobs)

            if redis:  # Only update the database if it's connected
                print(f"Adding {final_filtered_count} new job URLs to the database...")
                for job in final_filtered_jobs:
                    redis.set(job["url"], "seen", ex=2592000)  # 30 days

        # --- 5. ALWAYS send a status update message ---
        stats = {
            "total_found": total_jobs_from_api,
            "new_unseen": new_unseen_count,
            "final_filtered": final_filtered_count,
        }
        if DISCORD_WEBHOOK_URL:
            send_status_update(DISCORD_WEBHOOK_URL, stats)

        # --- 6. Respond to the HTTP request ---
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "success", "found_jobs": final_filtered_count}
            ).encode("utf-8")
        )
