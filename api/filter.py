# api/filter.py


def filter_jobs(jobs):
    """
    Filters a list of job dictionaries based on predefined keywords.

    Args:
        jobs (list): A list of job dictionaries, where each dictionary
                     is expected to have a 'title' key.

    Returns:
        list: A new list containing only the jobs that match the criteria.
    """
    # Keywords for roles you ARE interested in.
    # These are not case-sensitive.
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

    # Keywords for roles you ARE NOT interested in.
    # This helps eliminate common false positives.
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
    ]

    filtered_jobs = []
    for job in jobs:
        # Ensure the job has a title, otherwise skip it.
        if not job.get("title"):
            continue

        title_lower = job["title"].lower()
        description_lower = job.get(
            "description", ""
        ).lower()  # Also check description if available
        full_text = title_lower + " " + description_lower

        # --- Filtering Logic ---

        # 1. Check for negative keywords first to quickly eliminate irrelevant jobs.
        if any(neg_keyword in full_text for neg_keyword in negative_keywords):
            continue  # Skip to the next job if a negative keyword is found

        # 2. If no negative keywords are found, check for positive keywords.
        if any(pos_keyword in full_text for pos_keyword in positive_keywords):
            filtered_jobs.append(
                job
            )  # Add the job if it contains at least one positive keyword

    return filtered_jobs
