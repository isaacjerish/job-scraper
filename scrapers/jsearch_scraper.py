# scrapers/jsearch_scraper.py

import requests


def scrape_jsearch(api_key):
    print("--- Running JSearch Scraper with Multi-Query Strategy ---")

    search_queries = [
        "embedded systems intern",
        "firmware engineer intern",
        "systems programming intern",
        "vlsi design intern",
        "asic verification intern",
        "rtos engineer intern",
        "computer architecture intern",
        "low level software intern",
        "computer engineering intern",
        "software engineering intern",
        "electrical engineering intern",
    ]

    all_jobs = []
    seen_urls = set()

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

    for query in search_queries:
        print(f"  > Searching for: '{query}'")
        querystring = {
            "query": f"{query} in USA",
            "page": "1",
            "num_pages": "1",
            "employment_types": "INTERN,CONTRACTOR",
            "date_posted": "month",
        }

        try:
            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])

                if not jobs:
                    continue

                for job in jobs:
                    job_url = job.get("job_apply_link")
                    if job_url and job_url not in seen_urls:
                        all_jobs.append(
                            {
                                "title": job.get("job_title"),
                                "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(
                                    ", "
                                ),
                                "url": job_url,
                                "company": job.get("employer_name"),
                                "posted_at": job.get("job_posted_at_timestamp"),
                            }
                        )
                        seen_urls.add(job_url)
            else:
                print(
                    f"  > Error for query '{query}': {response.status_code} - {response.text}"
                )

        except requests.exceptions.RequestException as e:
            print(f"  > Exception for query '{query}': {e}")

    return all_jobs
