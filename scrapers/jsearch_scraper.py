# scrapers/jsearch_scraper.py

import requests


def scrape_jsearch(api_key):
    """
    Scrapes the JSearch API for jobs based on a set of keywords.
    Now also fetches the timestamp for manual filtering.
    """
    all_jobs = []

    query = (
        '("embedded systems" OR "firmware" OR "rtos" OR "c++" OR "systems programming" '
        'OR "device drivers" OR "kernel" OR "verilog" OR "vlsi" OR "fpga" OR "asic" '
        'OR "soc" OR "computer architecture" OR "cpu" OR "gpu" OR "compiler" OR "operating system") '
        "(internship OR co-op)"
    )

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "employment_types": "INTERN,CONTRACTOR",
        "date_posted": "week",  # Get jobs from the last week to ensure we have a good pool
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
                # Add the timestamp to the dictionary we create
                all_jobs.append(
                    {
                        "title": job.get("job_title"),
                        "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(
                            ", "
                        ),
                        "url": job.get("job_apply_link"),
                        "company": job.get("employer_name"),
                        "posted_at": job.get("job_posted_at_timestamp"),  # <-- NEW
                    }
                )
        else:
            print(f"Error from JSearch API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to JSearch API: {e}")

    return all_jobs
