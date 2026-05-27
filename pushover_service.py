import os

import requests


PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_TITLE = "Availability Update"

def _build_payload(tracker_name, message, app_token, user_key, device, priority, sound=None):
    payload = {
        "token": app_token,
        "user": user_key,
        "title": PUSHOVER_TITLE,
        "message": f"{message}",
    }
    if device:
        payload["device"] = device
    if sound:
        payload["sound"] = sound
    if priority:
        payload["priority"] = priority
    return payload


def send_notifications(data):
    app_token = os.getenv("pushover_app_token")
    user_key = os.getenv("pushover_user_key")
    device = 'iphone17'
    priority = 1

    if not app_token or not user_key:
        print("Pushover credentials are missing")
        return

    sent_count = 0
    for tracker_name, raw_message in data.items():
        if not raw_message:
            continue

        message = str(raw_message).strip()
        if not message:
            continue

        payload = _build_payload(
            tracker_name,
            message,
            app_token,
            user_key,
            device,
            priority,
        )

        try:
            response = requests.post(PUSHOVER_API_URL, data=payload, timeout=10)
            response.raise_for_status()
            print(f"Pushover notification sent for {tracker_name}")
            sent_count += 1
        except requests.RequestException as exc:
            print(f"Failed to send Pushover notification for {tracker_name}: {exc}")

    if sent_count == 0:
        print("No new content to send to Pushover.")
