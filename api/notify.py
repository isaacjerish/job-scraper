# api/notify.py

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
    """
    Sends a list of jobs to a Discord channel using a webhook.
    Highlights jobs from a predefined list of top companies.
    """
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
                embed_color = "FFD700"  # Gold
                embed_title = f"⭐ {job.get('title', 'No Title')}"
            else:
                embed_color = "03b2f8"  # Blue
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


def send_status_update(webhook_url, stats):
    """
    Sends a status update to Discord, even if no new jobs are found.

    Args:
        webhook_url (str): The URL of the Discord webhook.
        stats (dict): A dictionary containing run statistics.
    """
    if not webhook_url:
        return

    webhook = DiscordWebhook(url=webhook_url)

    # Use a different color for status updates to distinguish them
    embed = DiscordEmbed(
        title="✅ Job Scraper Status Update",
        color="2ECC71",  # Green color for a successful run
    )
    embed.set_author(name="Cron Job Report")
    embed.set_timestamp()

    # Add the statistics as fields in the embed
    embed.add_embed_field(
        name="Jobs Found by API", value=str(stats["total_found"]), inline=True
    )
    embed.add_embed_field(
        name="New (Unseen) Jobs", value=str(stats["new_unseen"]), inline=True
    )
    embed.add_embed_field(
        name="Relevant New Jobs", value=str(stats["final_filtered"]), inline=True
    )

    if stats["final_filtered"] == 0:
        embed.description = "No new relevant job postings found on this run. Everything is working correctly."
    else:
        embed.description = (
            f"Successfully found and sent {stats['final_filtered']} new job posting(s)!"
        )

    webhook.add_embed(embed)

    try:
        response = webhook.execute()
        if response.status_code in [200, 204]:
            print("Successfully sent status update to Discord.")
        else:
            print(
                f"Error sending status update to Discord: {response.status_code}, {response.content}"
            )
    except Exception as e:
        print(f"An exception occurred while sending status update to Discord: {e}")
