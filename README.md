# Personalised Low-Level & Embedded Internship Scraper

## 🚀 Overview

While excellent resources like the [Simplify](https://github.com/SimplifyJobs/Summer2025-Internships) repository cover general Software Engineering (SWE) internships extensively, there's a noticeable gap for students passionate about hardware-adjacent and low-level systems. This project was created to fill that niche.

It's a highly-specialized, automated job scraper designed specifically to find internship and co-op opportunities in embedded systems, firmware, systems programming, and VLSI. It leverages the JSearch API to cast a wide net across major job boards, then applies a series of strict, custom filters to ensure only the most relevant, recent listings are delivered directly to a Discord channel.

The system is built to be deployed as a serverless function on Vercel and is triggered by an external cron job, creating a "set it and forget it" job alert system tailored for the next generation of low-level engineers.

## ✨ Features

* **Interest-Based Scraping**: Uses the JSearch API to find jobs based on a curated list of keywords like "embedded systems", "firmware", "RTOS", "C++", "Verilog", etc.

* **Strict Recency Filtering**: Manually filters API results to ensure only jobs posted within the last 3 days are considered, providing fresh and actionable listings.

* **Intelligent De-duplication**: Utilizes a Vercel KV (Upstash Redis) database to remember which jobs have already been sent, preventing repeat notifications.

* **Automated Notifications**: Delivers new job listings directly to a Discord channel via a webhook.

* **Highlighted Alerts**: Automatically identifies and highlights listings from top-tier tech companies with a ⭐ emoji and a different color for high visibility.

* **Serverless & Cost-Effective**: Designed to run on Vercel's free Hobby tier, making it a powerful tool with no hosting costs.

## 🛠️ Tech Stack

* **Backend**: Python

* **Deployment**: Vercel Serverless Functions

* **Primary Data Source**: [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)

* **Database (for De-duplication)**: Vercel KV (powered by Upstash Redis)

* **Notifications**: Discord Webhooks

* **Automation**: External Cron Job service (e.g., [Cron-Job.org](https://cron-job.org/))

## ⚙️ Setup and Installation

Follow these steps to get the scraper running.

### 1. Clone the Repository

First, get the code onto your local machine.


git clone <your-repository-url>
cd job-scraper


### 2. Create a Python Virtual Environment

It's best practice to use a virtual environment to manage project dependencies.


Create the virtual environment
python3 -m venv venv

Activate it (on macOS/Linux)
source venv/bin/activate


### 3. Install Dependencies

Install all the necessary Python libraries from the `requirements.txt` file.


pip install -r requirements.txt


## 🔧 Configuration

The scraper relies on environment variables for its API keys and secrets. **Do not hardcode these into your files.**

### 1. Get API Keys

* **JSearch API Key**:

  1. Go to the [JSearch API page on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch).

  2. Sign up for a free account and subscribe to the **FREE** "Basic" plan.

  3. On the "Endpoints" tab, find your `X-RapidAPI-Key`.

* **Discord Webhook URL**:

  1. In your Discord server, go to `Server Settings` > `Integrations` > `Webhooks`.

  2. Click "New Webhook", give it a name, choose a channel, and copy the **Webhook URL**.

### 2. Set Environment Variables on Vercel

When you deploy to Vercel, add the following in your project's `Settings` > `Environment Variables`:

| Key | Value | 
 | ----- | ----- | 
| `JSEARCH_API_KEY` | Your key from RapidAPI | 
| `DISCORD_WEBHOOK_URL` | Your webhook URL from Discord | 

### 3. Set up Vercel KV Database

1. In your Vercel project dashboard, go to the **Storage** tab.

2. Select **Upstash for Redis** from the marketplace and follow the prompts to create a new database.

3. **Crucially, connect the new database to your `job-scraper` project.**

4. Vercel will automatically add the required database credentials (`KV_REST_API_URL`, `KV_REST_API_TOKEN`, etc.) to your environment variables.

## 🚀 Deployment & Automation

### Deployment

Deployment is handled automatically by Vercel's Git integration.

1. Push your code to a GitHub/GitLab/Bitbucket repository.
2. Import the repository as a new project on Vercel.
3. Configure the environment variables as described above.
4. Every time you push a new commit to your main branch, Vercel will automatically build and deploy the changes.

### Automation

The scraper function only runs when its URL is visited. Use a free cron job service to automate this.

1. Go to [Cron-Job.org](https://cron-job.org/) and create a free account.
2. Create a new cronjob.
3. **URL:** Enter your full Vercel deployment URL: `https://<your-project-name>.vercel.app/api/scrape`
4. **Schedule:** Set it to run every **15 or 30 minutes**.
5. Save the cronjob.

Your scraper is now fully automated!
