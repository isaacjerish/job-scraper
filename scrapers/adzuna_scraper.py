# scrapers/adzuna_scraper.py

import requests


def scrape_adzuna(app_id, api_key):
    """
    Scrapes the Adzuna API for jobs based on a set of keywords.

    Args:
        app_id (str): Your Adzuna Application ID.
        api_key (str): Your Adzuna API Key.

    Returns:
        list: A list of job dictionaries found from the API call.
    """
    all_jobs = []

    # Keywords to search for. Adzuna is smart about handling these.
    keywords = [
        "embedded systems",
        "firmware",
        "rtos",
        "c++",
        "c language",
        "systems programming",
        "device drivers",
        "kernel",
        "verilog",
        "systemverilog",
        "vlsi",
        "fpga",
        "asic",
        "low level software",
    ]

    # --- Corrected URL Construction ---
    # Base URL for the Adzuna API endpoint
    base_url = "http://api.adzuna.com/v1/api/jobs/us/search/1"

    # Parameters for the API request. Using a dictionary is cleaner and safer,
    # as the 'requests' library handles URL encoding automatically.
    # You can change 'us' to 'gb' (UK), 'ca' (Canada), etc.
    params = {
        "app_id": app_id,
        "app_key": api_key,
        "results_per_page": 50,
        "what_or": " ".join(keywords),  # Join keywords with a space for the query
        "what_and": "internship intern co-op",  # Ensure it's an internship/co-op
        "sort_by": "date",
        "content-type": "application/json",
    }

    try:
        # Make the GET request with the base URL and parameters
        response = requests.get(base_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])

            for job in jobs:
                # Format the job data to be consistent with our other scrapers
                all_jobs.append(
                    {
                        "title": job.get("title"),
                        "location": job.get("location", {}).get("display_name", "N/A"),
                        "url": job.get(
                            "redirect_url"
                        ),  # Adzuna provides a redirect URL
                        "company": job.get("company", {}).get("display_name", "N/A"),
                    }
                )
        else:
            print(f"Error from Adzuna API: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error making request to Adzuna API: {e}")

    return all_jobs
