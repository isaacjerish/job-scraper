# api/notify.py

from discord_webhook import DiscordWebhook, DiscordEmbed


def send_to_discord(webhook_url, jobs):
    """
    Sends a list of jobs to a Discord channel using a webhook.

    Args:
        webhook_url (str): The URL of the Discord webhook.
        jobs (list): A list of filtered job dictionaries to be sent.
    """
    # You can send multiple embeds in one message, but Discord has a limit of 10.
    # This will send one message containing all the job embeds.
    # For a large number of jobs, you might want to send them in batches.
    webhook = DiscordWebhook(url=webhook_url)

    if not jobs:
        print("No new jobs to notify.")
        return

    print(f"Sending {len(jobs)} new jobs to Discord...")

    for job in jobs:
        # Create an 'embed' for each job. Embeds are rich message formats in Discord.
        embed = DiscordEmbed(
            title=job.get("title", "No Title"),
            description=f"**Location:** {job.get('location', 'N/A')}",
            color="03b2f8",  # A nice blue color, you can change this
        )

        # Set a clear author for the embed
        embed.set_author(name="New Internship/Co-op Found!")

        # Add a clickable link to the job posting
        if job.get("url"):
            embed.add_embed_field(
                name="Apply Now", value=f"[Click Here to Apply]({job['url']})"
            )
        else:
            embed.add_embed_field(name="Apply Now", value="URL not found")

        # Add the timestamp for when the notification was sent
        embed.set_timestamp()

        # Add the fully created embed to our webhook message
        webhook.add_embed(embed)

    # Execute the webhook to send the message to Discord.
    # The response will contain the status code from Discord's server.
    try:
        response = webhook.execute()
        if response.status_code == 200 or response.status_code == 204:
            print("Successfully sent notifications to Discord.")
        else:
            print(
                f"Error sending to Discord: {response.status_code}, {response.content}"
            )
    except Exception as e:
        print(f"An exception occurred while sending to Discord: {e}")
