# scrapers/jsearch_scraper.py

import requests


def scrape_jsearch(api_key):
    """
    Scrapes the JSearch API for jobs based on a set of keywords.

    Args:
        api_key (str): Your JSearch API Key from RapidAPI.

    Returns:
        list: A list of job dictionaries found from the API call.
    """
    print("--- DEBUG: Running JSearch Scraper V1 ---")
    all_jobs = []

    # JSearch is powerful and can handle complex queries well.
    # We are searching for internships posted in the last week to ensure we get results.
    query = (
        '("embedded systems" OR "firmware" OR "rtos" OR "c++" OR "systems programming" '
        'OR "device drivers" OR "kernel" OR "verilog" OR "vlsi" OR "fpga" OR "asic") '
        "internship"
    )

    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "employment_types": "INTERN",
        "date_posted": "week",  # Broaden to 'week' to ensure we get results first
    }

    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

    try:
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get("data", [])

            if not jobs:
                print("--- DEBUG: JSearch API returned 0 jobs. ---")
                return []

            for job in jobs:
                # Format the job data to be consistent with our application
                all_jobs.append(
                    {
                        "title": job.get("job_title"),
                        "location": f"{job.get('job_city', '')}, {job.get('job_state', '')}".strip(
                            ", "
                        ),
                        "url": job.get("job_apply_link"),
                        "company": job.get("employer_name"),
                    }
                )
        else:
            print(f"Error from JSearch API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to JSearch API: {e}")

    return all_jobs
