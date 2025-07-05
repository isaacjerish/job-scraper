# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os

# Import the new JSearch scraper
from scrapers.jsearch_scraper import scrape_jsearch

# Import our helper functions (filter and notify)
from api.filter import filter_jobs
from api.notify import send_to_discord

# --- Get NEW JSearch API Key and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")  # <-- NEW KEY


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        all_jobs = []

        # --- Main scraping step using JSearch ---
        if JSEARCH_API_KEY:
            all_jobs = scrape_jsearch(JSEARCH_API_KEY)
        else:
            print("JSearch API Key not found. Cannot perform search.")

        # --- Filtering and Notification ---
        # The same filter works perfectly on the JSearch results
        final_filtered_jobs = filter_jobs(all_jobs)

        print(f"Found {len(final_filtered_jobs)} relevant jobs after filtering.")

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
