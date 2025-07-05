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

            # --- NEW DEBUGGING STATEMENTS ---
            print(
                f"--- DEBUG: Found {len(all_jobs)} jobs from Adzuna BEFORE filtering. ---"
            )
            if all_jobs:
                print("--- DEBUG: First 5 job titles from Adzuna: ---")
                for i, job in enumerate(all_jobs[:5]):
                    print(f"  {i + 1}: {job.get('title')}")
            # --- END DEBUGGING STATEMENTS ---

        else:
            print("Adzuna credentials not found. Cannot perform search.")

        # --- Filtering and Notification ---
        final_filtered_jobs = filter_jobs(all_jobs)

        print(f"Found {len(final_filtered_jobs)} jobs after final filtering.")

        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
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
