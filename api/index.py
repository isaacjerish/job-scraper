# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os

# We ONLY need the Adzuna scraper now
from scrapers.adzuna_scraper import scrape_adzuna

# Import our helper functions
from api.filter import filter_jobs
from api.notify import send_to_discord

# --- Get API Keys and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.environ.get("ADZUNA_API_KEY")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        all_jobs = []

        # --- The ONLY scraping step now is the wide-net Adzuna search ---
        if ADZUNA_APP_ID and ADZUNA_API_KEY:
            print("Starting interest-based job search with Adzuna...")
            all_jobs = scrape_adzuna(ADZUNA_APP_ID, ADZUNA_API_KEY)
            print(f"Found {len(all_jobs)} potential jobs from Adzuna.")
        else:
            print("Adzuna credentials not found. Cannot perform search.")

        # --- Filtering and Notification ---
        # Our existing filter will now work on this much smaller, more relevant list
        final_filtered_jobs = filter_jobs(all_jobs)

        print(f"Found {len(final_filtered_jobs)} jobs after final filtering.")

        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
            # The notifier will send the jobs in batches of 10
            send_to_discord(DISCORD_WEBHOOK_URL, final_filtered_jobs)

        # Respond to the HTTP request
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "success", "found_jobs": len(final_filtered_jobs)}
            ).encode("utf-8")
        )
