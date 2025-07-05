from fastapi import FastAPI
from api.greenhouse import scrape_greenhouse
from api.lever import scrape_lever
from utils.filters import is_relevant

app = FastAPI()


@app.get("/jobs")
def get_filtered_jobs():
    gh_jobs = scrape_greenhouse()
    lv_jobs = scrape_lever()
    all_jobs = gh_jobs + lv_jobs
    filtered = [job for job in all_jobs if is_relevant(job)]
    return {"jobs": filtered}
