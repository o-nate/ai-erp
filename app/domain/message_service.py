"""WhatsApp domain-specific functions"""

import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from typing import BinaryIO

import json
import requests

from dotenv import load_dotenv
from openai import OpenAI

from configs.logging_config import get_logger

from domain.agents.demo_agent import demo_agent

from schema import Audio, User


logger = get_logger(__name__)

load_dotenv()

WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

ALLOWED_USERS = [
    {
        "id": 1,
        "phone": "15857039796",
        "first_name": "Nate",
        "last_name": "Dos Santos",
        "role": "basic",
    },
    {
        "id": 2,
        "phone": "5521988702009",
        "first_name": "Laura",
        "last_name": "Lawrence",
        "role": "basic",
    },
]

llm = OpenAI()


def transcribe_audio_file(audio_file: BinaryIO | None) -> str:
    if not audio_file:
        return "No audio file provided"
    try:
        transcription = llm.audio.transcriptions.create(
            file=audio_file, model="whisper-1", response_format="text"
        )
        return transcription
    except Exception as e:
        raise ValueError("Error transcribing audio") from e


def transcribe_audio(audio: Audio) -> str:
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)
    with open(file_path, "rb") as audio_binary:
        transcription = transcribe_audio_file(audio_binary)
    try:
        os.remove(file_path)
    except Exception as e:
        logger.warning("Failed to delete file: %s", e)
    return transcription


def download_file_from_facebook(
    file_id: str, file_type: str, mime_type: str
) -> str | None:
    # Retrieve file URL to then submit a second GET request to download
    url = f"https://graph.facebook.com/v19.0/{file_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        download_url = response.json().get("url")

        response = requests.get(download_url, headers=headers)

        if response.status_code == 200:
            file_extension = mime_type.split("/")[-1].split(";")[0]
            file_path = f"{file_id}.{file_extension}"
            with open(file_path, "wb") as file:
                file.write(response.content)
            if file_type == "image" or file_type == "audio":
                return file_path

        raise ValueError(
            f"Failed to download file. Status code: {response.status_code}"
        )
    raise ValueError(
        f"Failed to retrieve download URL. Status code: {response.status_code}"
    )


def authenticate_user_by_phone_number(phone_number: str) -> User | None:
    for user in ALLOWED_USERS:
        if user["phone"] == phone_number:
            return User(**user)
    return None


def send_whatsapp_message(to, message, template=True) -> dict:
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + WHATSAPP_API_KEY,
        "Content-Type": "application/json",
    }
    if not template:
        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": "hello_world", "language": {"code": "en_US"}},
        }

    logger.info("Attempting to send message to WhatsApp API.")
    logger.debug("API URL: %s", url)
    logger.debug("Headers: %s", headers)
    logger.debug("Payload: %s", data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        logger.info("Received response from WhatsApp API.")
        logger.info("Status Code: %s", response.status_code)
        logger.info("Response Body: %s", response.text)

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error sending message to WhatsApp API: %s", e)
        # Depending on desired behavior, you might want to re-raise or return an error indicator
        raise  # Re-raise the exception for now to make it visible


def respond_and_send_message(user_message: str, user: User) -> None:
    agent = demo_agent
    response = agent.run(user_message, user.id)
    send_whatsapp_message(user.phone, response, template=False)
    logger.info(
        "Sent message to user %s %s (%s)", user.first_name, user.last_name, user.phone
    )
    logger.info("Message: %s", response)


def main() -> None:
    user = authenticate_user_by_phone_number("15857039796")
    logger.debug("User: %s", user)
    respond_and_send_message("What are my expenses to date?", user=user)


if __name__ == "__main__":
    main()
