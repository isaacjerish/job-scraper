from http.server import BaseHTTPRequestHandler
import json
import os
from upstash_redis import Redis
import time

from scrapers.jsearch_scraper import scrape_jsearch

from api.filter import filter_jobs
from api.notify import send_to_discord, send_daily_report

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY")

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

        all_jobs = scrape_jsearch(JSEARCH_API_KEY)
        total_from_api = len(all_jobs)
        print(f"JSearch API returned {total_from_api} total jobs.")

        three_days_ago_timestamp = int(time.time()) - (3 * 24 * 60 * 60)
        recent_jobs = []
        for job in all_jobs:
            if job.get("posted_at") and job["posted_at"] > three_days_ago_timestamp:
                recent_jobs.append(job)
        recent_count = len(recent_jobs)
        print(f"Found {recent_count} jobs posted in the last 3 days.")

        new_unseen_jobs = []
        if redis:
            for job in recent_jobs:
                job_url = job.get("url")
                if job_url and not redis.exists(job_url):
                    new_unseen_jobs.append(job)
        else:
            new_unseen_jobs = recent_jobs
        new_unseen_count = len(new_unseen_jobs)
        print(f"Found {new_unseen_count} new, unseen jobs.")

        final_filtered_jobs = filter_jobs(new_unseen_jobs)
        final_filtered_count = len(final_filtered_jobs)
        print(f"Found {final_filtered_count} relevant new jobs after final filtering.")

        if final_filtered_jobs and DISCORD_WEBHOOK_URL:
            send_to_discord(DISCORD_WEBHOOK_URL, final_filtered_jobs)
            if redis:
                print(f"Adding {final_filtered_count} new job URLs to the database...")
                for job in final_filtered_jobs:
                    redis.set(job["url"], "seen", ex=2592000)

        stats = {
            "total_from_api": total_from_api,
            "recent_count": recent_count,
            "new_unseen_count": new_unseen_count,
            "final_filtered": final_filtered_count,
        }
        if DISCORD_WEBHOOK_URL:
            send_daily_report(DISCORD_WEBHOOK_URL, stats)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {"status": "success", "found_jobs": final_filtered_count}
            ).encode("utf-8")
        )
