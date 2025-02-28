import requests
import os
from src.helpers.logger import logger

# Load environment variables from .env file


# Retrieve Telegram bot credentials from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


def inform_me(message_text):
    """
    Send a message to the configured Telegram channel.
    :param message_text: The message to send.
    """
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": f"{TELEGRAM_CHANNEL_ID}", "text": message_text}
            headers = {"Content-Type": "application/json"}

            logger.info("Sending message to Telegram...")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for failed requests

            logger.info("Message sent successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message: {e}")
    else:
        logger.error("Telegram credentials not found in environment variables")
