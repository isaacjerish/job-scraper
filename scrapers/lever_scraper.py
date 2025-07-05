import requests
from bs4 import BeautifulSoup


def scrape_lever(company_list):
    all_jobs = []
    for company in company_list:
        try:
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json()
                for job in jobs:
                    all_jobs.append(
                        {
                            "title": job.get("text"),
                            "location": job.get("categories", {}).get(
                                "location", "N/A"
                            ),
                            "url": job.get("hostedUrl"),
                        }
                    )
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {company}: {e}")
    return all_jobs
