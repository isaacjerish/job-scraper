# api/filter.py


def filter_jobs(jobs):
    """
    Filters a list of job dictionaries based on predefined keywords.
    This acts as a final quality check.
    """
    positive_keywords = [
        "embedded",
        "firmware",
        "low-level",
        "vlsi",
        "c++",
        "c",
        "python",
        "rtos",
        "bare-metal",
        "systems programming",
        "device driver",
        "digital design",
        "verilog",
        "systemverilog",
        "fpga",
        "asic",
        "kernel",
        "bootloader",
        "microcontroller",
        "mcu",
    ]

    # Negative keywords to filter out senior or unrelated roles.
    negative_keywords = [
        "frontend",
        "front-end",
        "web development",
        "javascript",
        "html",
        "css",
        "data science",
        "machine learning",
        "analyst",
        "react",
        "angular",
        "vue",
        "fullstack",
        "full-stack",
        "senior",
        "sr.",
        "lead",
        "staff",
        "principal",
        "manager",
        "phd",
    ]

    filtered_jobs = []
    for job in jobs:
        if not job.get("title"):
            continue

        title_lower = job["title"].lower()

        # The strict check for "intern" has been removed. We now trust the API
        # to send us internships and use this filter as a final quality pass.

        # 1. Check for negative keywords to remove obvious mismatches.
        if any(neg_keyword in title_lower for neg_keyword in negative_keywords):
            continue

        # 2. Check for positive keywords to ensure relevance to your interests.
        if any(pos_keyword in title_lower for pos_keyword in positive_keywords):
            filtered_jobs.append(job)

    return filtered_jobs
