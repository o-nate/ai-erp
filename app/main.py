"""Main script"""

import os
import threading

from typing_extensions import Annotated

import uvicorn

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, FastAPI, Query, Request

from domain import message_service
from configs.logging_config import get_logger
from schema import Audio, Image, Message, Payload, User

load_dotenv()

logger = get_logger(__name__)

VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
IS_DEV_ENVIRONMENT = os.getenv("ENVIRONMENT").lower() == "dev"

app = FastAPI(
    title="WhatsApp AI ERP",
    version="0.1.0",
    openapi_url="/openapi.json" if IS_DEV_ENVIRONMENT else None,
    docs_url="/docs" if IS_DEV_ENVIRONMENT else None,
    redoc_url="/redoc" if IS_DEV_ENVIRONMENT else None,
    swagger_ui_oauth2_redirect_url=(
        "/docs/oauth2-redirect" if IS_DEV_ENVIRONMENT else None
    ),
)


@app.get("/")
def verify_whatsapp(
    hub_mode: str = Query(
        "subscribe", description="The mode of the webhook", alias="hub.mode"
    ),
    hub_challenge: int = Query(
        ..., description="The challenge to verify the webhook", alias="hub.challenge"
    ),
    hub_verify_token: str = Query(
        ..., description="The verification token", alias="hub.verify_token"
    ),
) -> int | None:
    if hub_mode == "subscribe" and hub_verify_token == VERIFICATION_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readiness")
def readiness() -> dict[str, str]:
    return {"status": "ready"}


def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]


def get_current_user(
    message: Annotated[Message, Depends(parse_message)] | None,
) -> User | None:
    if not message:
        return None
    return message_service.authenticate_user_by_phone_number(message.from_)


def parse_audio_file(
    message: Annotated[Message, Depends(parse_message)],
) -> Audio | None:
    if message and message.type == "audio":
        return message.audio
    return None


def parse_image_file(
    message: Annotated[Message, Depends(parse_message)],
) -> Image | None:
    if message and message.type == "image":
        return message.image
    return None


def message_extractor(
    message: Annotated[Message, Depends(parse_message)] | None,
    audio: Annotated[Audio, Depends(parse_audio_file)] | None,
):
    if audio:
        return message_service.transcribe_audio(audio)
    if message and message.text:
        return message.text.body
    return None


@app.post("/", status_code=200)
async def receive_whatsapp(
    request: Request,
    payload: Payload,
) -> dict[str, str]:
    logger.info("Message received")

    try:
        # Log the raw incoming request body
        body = await request.json()
        logger.info(f"Received webhook payload: {body}")

        # Use existing parsing logic to extract data from the payload
        message = parse_message(payload)
        user = get_current_user(message)
        audio = parse_audio_file(message)
        image = parse_image_file(message)
        user_message = message_extractor(message, audio)

    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")
        # Re-raise the exception or return an appropriate error response if needed
        raise HTTPException(status_code=400, detail=f"Error processing payload: {e}")

    if not user and not user_message and not image:
        return {"status": "ok"}
    if not user:
        logger.warning("Unauthorized: User not found for incoming message.")
        raise HTTPException(status_code=401, detail="Unauthorized")
    if image:
        logger.info("Image received (processing not implemented)")
        return {"status": "image received"}
    if user_message:
        logger.info(
            "Message received from %s %s (%s)",
            user.first_name,
            user.last_name,
            user.phone,
        )
        thread = threading.Thread(
            target=message_service.respond_and_send_message, args=(user_message, user)
        )
        thread.daemon = True
        thread.start()
        return {"status": "message processed"}

    # Fallback for unhandled message types if any reach this point
    logger.info("Received unhandled message type or content.")
    return {"status": "unhandled"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
