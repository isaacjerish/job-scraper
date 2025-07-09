def filter_jobs(jobs):
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
        "soc",
        "system on chip",
        "computer architecture",
        "cpu",
        "gpu",
        "compiler",
        "electrical engineer",
        "operating system",
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

        # 1. Check for negative keywords to remove obvious mismatches.
        if any(neg_keyword in title_lower for neg_keyword in negative_keywords):
            continue

        # 2. Check for positive keywords to ensure relevance to your interests.
        if any(pos_keyword in title_lower for pos_keyword in positive_keywords):
            filtered_jobs.append(job)

    return filtered_jobs
