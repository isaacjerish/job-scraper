from discord_webhook import DiscordWebhook, DiscordEmbed
import time

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


def send_daily_report(webhook_url, stats):
    if not webhook_url:
        return

    webhook = DiscordWebhook(url=webhook_url)

    if stats["final_filtered"] > 0:
        report_title = f"✅ Daily Report: {stats['final_filtered']} New Jobs Found!"
        report_color = "2ECC71"  # Green
    else:
        report_title = "✅ Daily Report: No New Jobs"
        report_color = "757f8d"  # Grey

    embed = DiscordEmbed(title=report_title, color=report_color)
    embed.set_author(name="Scheduled Job Scraper Run")
    embed.set_timestamp()

    embed.add_embed_field(
        name="API Results", value=str(stats["total_from_api"]), inline=True
    )
    embed.add_embed_field(
        name="Recent (3 days)", value=str(stats["recent_count"]), inline=True
    )
    embed.add_embed_field(
        name="New & Unseen", value=str(stats["new_unseen_count"]), inline=True
    )

    if stats["final_filtered"] == 0:
        embed.description = "The scraper ran successfully. No new relevant job postings were found today."
    else:
        embed.description = f"Successfully found and sent **{stats['final_filtered']}** new job posting(s)!"

    webhook.add_embed(embed)

    try:
        response = webhook.execute()
        if response.status_code in [200, 204]:
            print("Successfully sent daily report to Discord.")
        else:
            print(
                f"Error sending daily report to Discord: {response.status_code}, {response.content}"
            )
    except Exception as e:
        print(f"An exception occurred while sending daily report to Discord: {e}")
