import logging
import os
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

def send_notification(
    title: dict,
    message: dict,
    data: list = None,
):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}",
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": message},
        "included_segments": ["Subscribed Users"],
        "external_id": str(uuid.uuid4()),
        "channel_for_external_user_ids": "push"
    }

    if data:
        payload["data"] = data

    response = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers=headers,
        json=payload,
        timeout=10,
    )

    if response.status_code == 200:
        logger.info("Notification sent successfully.")
    else:
        logger.error(
            "Failed to send notification: %d - %s",
            response.status_code,
            response.text,
        )

    return response.json()


def main():
    response = send_notification(
        title="Test Notification",
        message="This is a test notification from OneSignal service.",
    )
    print(response)


if __name__ == "__main__":
    main()
