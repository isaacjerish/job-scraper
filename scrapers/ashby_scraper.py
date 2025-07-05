import requests


def scrape_ashby(company_list):
    all_jobs = []
    for company in company_list:
        try:
            url = f"https://api.ashbyhq.com/v1/jobs?ashbyApiToken={company}"
            response = requests.get(url)
            if response.status_code == 200:
                jobs = response.json().get("results", [])
                for job in jobs:
                    all_jobs.append(
                        {
                            "title": job.get("title"),
                            "location": job.get("location", "N/A"),
                            "url": job.get("jobUrl"),
                        }
                    )
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {company}: {e}")
    return all_jobs
