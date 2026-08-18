import requests


DISCORD_CONTENT_LIMIT = 2000
DISCORD_TITLE = "Availability Update"


def _build_messages(tracker_name, message):
    header = ""
    chunk_size = DISCORD_CONTENT_LIMIT - len(header)
    return [
        header + message[start : start + chunk_size]
        for start in range(0, len(message), chunk_size)
    ]


def send_notifications(data, webhook_url, channel_alias):
    had_content = False
    for tracker_name, raw_message in data.items():
        if not raw_message or not (message := str(raw_message).strip()):
            continue
        had_content = True

        try:
            for content in _build_messages(tracker_name, message):
                response = requests.post(
                    webhook_url,
                    params={"wait": "true"},
                    json={
                        "content": content,
                        "allowed_mentions": {"parse": []},
                    },
                    timeout=10,
                )
                response.raise_for_status()
            print(f"Discord notification sent for {tracker_name} to {channel_alias}")
        except requests.RequestException as exc:
            print(
                f"Failed to send Discord notification for {tracker_name} "
                f"to {channel_alias}: {exc}"
            )

    if not had_content:
        print(f"No new content to send to Discord channel {channel_alias}.")
