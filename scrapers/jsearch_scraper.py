# scrapers/jsearch_scraper.py

import requests


def scrape_jsearch(api_key):
    all_jobs = []
    query = "embedded software engineering internship OR firmware engineering internship OR systems engineering internship or software engineering internship or electrical engineering internship"

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "5",
        "employment_types": "INTERN,CONTRACTOR",
        "date_posted": "month",
    }

    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

    try:
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get("data", [])

            if not jobs:
                return []

            for job in jobs:
                all_jobs.append(
                    {
                        "title": job.get("job_title"),
                        "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(
                            ", "
                        ),
                        "url": job.get("job_apply_link"),
                        "company": job.get("employer_name"),
                        "posted_at": job.get("job_posted_at_timestamp"),
                    }
                )
        else:
            print(f"Error from JSearch API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to JSearch API: {e}")

    return all_jobs
