from discord_webhook import DiscordWebhook, DiscordEmbed
import time

# List of top-tier companies to highlight in notifications
BIG_TECH_COMPANIES = [
    "apple",
    "google",
    "meta",
    "amazon",
    "microsoft",
    "netflix",
    "nvidia",
    "amd",
    "intel",
    "qualcomm",
    "tesla",
    "spacex",
    "openai",
    "anthropic",
    "databricks",
    "snowflake",
    "cloudflare",
]


def send_to_discord(webhook_url, jobs):
    if not jobs:
        return

    print(f"Sending {len(jobs)} new jobs to Discord in batches...")

    job_chunks = [jobs[i : i + 10] for i in range(0, len(jobs), 10)]

    for chunk in job_chunks:
        webhook = DiscordWebhook(url=webhook_url)

        for job in chunk:
            company_name = job.get("company", "").lower()
            is_big_tech = any(tech_co in company_name for tech_co in BIG_TECH_COMPANIES)

            if is_big_tech:
                embed_color = "FFD700"
                embed_title = f"⭐ {job.get('title', 'No Title')}"
            else:
                embed_color = "03b2f8"
                embed_title = job.get("title", "No Title")

            embed = DiscordEmbed(
                title=embed_title,
                description=f"**Location:** {job.get('location', 'N/A')}",
                color=embed_color,
            )
            embed.set_author(name="New Internship/Co-op Found!")

            if job.get("url"):
                embed.add_embed_field(
                    name="Apply Now", value=f"[Click Here to Apply]({job['url']})"
                )
            else:
                embed.add_embed_field(name="Apply Now", value="URL not found")

            if job.get("company"):
                embed.add_embed_field(name="Company", value=job["company"])

            embed.set_timestamp()
            webhook.add_embed(embed)

        try:
            response = webhook.execute()
            if response.status_code in [200, 204]:
                print(f"Successfully sent a batch of {len(chunk)} jobs to Discord.")
            else:
                print(
                    f"Error sending batch to Discord: {response.status_code}, {response.content}"
                )

            time.sleep(1)

        except Exception as e:
            print(f"An exception occurred while sending a batch to Discord: {e}")
