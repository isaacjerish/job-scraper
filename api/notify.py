# api/notify.py

from discord_webhook import DiscordWebhook, DiscordEmbed
import time


def send_to_discord(webhook_url, jobs):
    """
    Sends a list of jobs to a Discord channel using a webhook.
    Handles Discord's 10-embed limit by sending jobs in batches.

    Args:
        webhook_url (str): The URL of the Discord webhook.
        jobs (list): A list of filtered job dictionaries to be sent.
    """
    if not jobs:
        print("No new jobs to notify.")
        return

    print(f"Sending {len(jobs)} new jobs to Discord in batches...")

    # Split the jobs list into chunks of 10
    job_chunks = [jobs[i : i + 10] for i in range(0, len(jobs), 10)]

    for chunk in job_chunks:
        # Create a new webhook object for each batch of 10 jobs
        webhook = DiscordWebhook(url=webhook_url)

        for job in chunk:
            # Create an 'embed' for each job.
            embed = DiscordEmbed(
                title=job.get("title", "No Title"),
                description=f"**Location:** {job.get('location', 'N/A')}",
                color="03b2f8",
            )
            embed.set_author(name="New Internship/Co-op Found!")

            if job.get("url"):
                embed.add_embed_field(
                    name="Apply Now", value=f"[Click Here to Apply]({job['url']})"
                )
            else:
                embed.add_embed_field(name="Apply Now", value="URL not found")

            # Add company name if available
            if job.get("company"):
                embed.add_embed_field(name="Company", value=job["company"])

            embed.set_timestamp()
            webhook.add_embed(embed)

        # Execute the webhook to send the current batch to Discord.
        try:
            response = webhook.execute()
            if response.status_code in [200, 204]:
                print(f"Successfully sent a batch of {len(chunk)} jobs to Discord.")
            else:
                # This will print the specific error if a batch fails
                print(
                    f"Error sending batch to Discord: {response.status_code}, {response.content}"
                )

            # Wait for a second between sending batches to be nice to Discord's API
            time.sleep(1)

        except Exception as e:
            print(f"An exception occurred while sending a batch to Discord: {e}")
