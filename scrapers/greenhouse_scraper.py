import requests
from bs4 import BeautifulSoup


def scrape_greenhouse(company_list):
    all_jobs = []
    for company in company_list:
        try:
            url = f"https://api.greenhouse.io/v1/boards/{company}/jobs"
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json().get("jobs", [])
                for job in jobs:
                    all_jobs.append(
                        {
                            "title": job.get("title"),
                            "location": job.get("location", {}).get("name", "N/A"),
                            "url": job.get("absolute_url"),
                        }
                    )
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {company}: {e}")
    return all_jobs
