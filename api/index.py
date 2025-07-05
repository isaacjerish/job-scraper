# api/index.py

from http.server import BaseHTTPRequestHandler
import json
import os

# Import all our scrapers
from scrapers.greenhouse_scraper import scrape_greenhouse
from scrapers.lever_scraper import scrape_lever
from scrapers.ashby_scraper import scrape_ashby
from scrapers.adzuna_scraper import scrape_adzuna  # <-- NEW

# Import our helper functions
from api.filter import filter_jobs
from api.notify import send_to_discord

# --- Get API Keys and Webhook from Environment Variables ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")  # <-- NEW
ADZUNA_API_KEY = os.environ.get("ADZUNA_API_KEY")  # <-- NEW


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # --- Comprehensive list of companies for targeted scraping ---
        # (This list is a great starting point and can be expanded)
        greenhouse_companies = [
            "nvidia",
            "amd",
            "intel",
            "qualcomm",
            "apple",
            "tesla",
            "spacex",
            "cruise",
            "waymo",
            "rivian",
            "lucidmotors",
            "zoox",
            "aurora",
            "microsoft",
            "amazon",
            "google",
            "meta",
            "cisco",
            "samsung",
            "sandia",
            "lockheedmartin",
            "northropgrumman",
            "raytheontechnologies",
            "boeing",
            "nasa",
            "jetpropulsionlaboratory",
            "draper",
            "palantir",
            "anduril",
            "shieldai",
        ]

        lever_companies = [
            "openai",
            "anthropic",
            "mistralai",
            "ramp",
            "brex",
            "rippling",
            "verkada",
            "samsara",
            "motional",
            "paloaltonetworks",
            "cloudflare",
            "databricks",
            "snowflake",
            "roblox",
            "instacart",
            "reddit",
        ]

        # Ashby is less common but we can add some known ones
        ashby_companies = []

        # --- Main Scraping Logic ---
        all_jobs = []

        print("Starting targeted company scraping...")
        all_jobs.extend(scrape_greenhouse(greenhouse_companies))
        all_jobs.extend(scrape_lever(lever_companies))
        all_jobs.extend(scrape_ashby(ashby_companies))

        print(f"Found {len(all_jobs)} jobs from targeted companies.")

        # --- NEW: Wide-net scraping with Adzuna ---
        if ADZUNA_APP_ID and ADZUNA_API_KEY:
            print("Starting wide-net scraping with Adzuna...")
            adzuna_jobs = scrape_adzuna(ADZUNA_APP_ID, ADZUNA_API_KEY)
            print(f"Found {len(adzuna_jobs)} jobs from Adzuna.")
            all_jobs.extend(adzuna_jobs)
        else:
            print("Adzuna credentials not found. Skipping wide-net scrape.")

        # --- NEW: De-duplicate jobs ---
        # This prevents getting multiple notifications for the same job
        # if it's found by both a targeted scraper and Adzuna.
        unique_jobs = []
        seen_urls = set()
        for job in all_jobs:
            url = job.get("url")
            if url and url not in seen_urls:
                unique_jobs.append(job)
                seen_urls.add(url)

        print(f"Found {len(unique_jobs)} unique jobs after de-duplication.")

        # --- Filtering and Notification ---
        # The same filter function works on the combined, unique list
        final_filtered_jobs = filter_jobs(unique_jobs)

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
