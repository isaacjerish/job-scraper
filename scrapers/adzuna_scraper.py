# scrapers/adzuna_scraper.py

import requests


def scrape_adzuna(app_id, api_key):
    """
    Scrapes the Adzuna API specifically for internships based on keywords.
    This version has the 3-day limit removed for broader testing.

    Args:
        app_id (str): Your Adzuna Application ID.
        api_key (str): Your Adzuna API Key.

    Returns:
        list: A list of job dictionaries found from the API call.
    """
    print("--- DEBUG: Running Adzuna scraper V4 (using 'what' parameter). ---")

    all_jobs = []

    # We will combine the keywords into a single string for the 'what' parameter
    keywords = "embedded systems firmware rtos c++ systems programming device drivers kernel verilog vlsi fpga asic"

    base_url = "http://api.adzuna.com/v1/api/jobs/us/search/1"

    params = {
        "app_id": app_id,
        "app_key": api_key,
        "results_per_page": 50,
        "what": keywords,  # Using the more standard 'what' parameter instead of 'what_or'
        "sort_by": "date",
        "contract_time": "intern",  # Still filtering for internships
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])

            for job in jobs:
                all_jobs.append(
                    {
                        "title": job.get("title"),
                        "location": job.get("location", {}).get("display_name", "N/A"),
                        "url": job.get("redirect_url"),
                        "company": job.get("company", {}).get("display_name", "N/A"),
                    }
                )
        else:
            # This will now show a proper JSON error from Adzuna if there is one.
            print(f"Error from Adzuna API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to Adzuna API: {e}")

    return all_jobs
