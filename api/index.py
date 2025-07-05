from http.server import BaseHTTPRequestHandler
import json
from scrapers.greenhouse_scraper import scrape_greenhouse
from scrapers.lever_scraper import scrape_lever
from scrapers.ashby_scraper import scrape_ashby
from .filter import filter_jobs
from .notify import send_to_discord
import os

# Get your Discord webhook URL from an environment variable
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Define the companies you want to scrape
        greenhouse_companies = [
            "company1",
            "company2",
        ]  # Add your target Greenhouse company IDs
        lever_companies = ["companyA", "companyB"]  # Add your target Lever company IDs
        ashby_companies = [
            "companyX",
            "companyY",
        ]  # Add your target Ashby company API tokens

        # Scrape all job boards
        all_jobs = []
        all_jobs.extend(scrape_greenhouse(greenhouse_companies))
        all_jobs.extend(scrape_lever(lever_companies))
        all_jobs.extend(scrape_ashby(ashby_companies))

        # Filter the jobs
        filtered_jobs = filter_jobs(all_jobs)

        # Send notifications
        if filtered_jobs and DISCORD_WEBHOOK_URL:
            send_to_discord(DISCORD_WEBHOOK_URL, filtered_jobs)

        # Respond to the HTTP request
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "success", "found_jobs": len(filtered_jobs)}).encode(
                "utf-8"
            )
        )
