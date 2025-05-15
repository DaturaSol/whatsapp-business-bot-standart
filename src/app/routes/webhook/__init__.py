"""Module responsible for WebHook route"""

from fastapi import APIRouter, Request, Response, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp import ClientSession
import logging
from pydantic import ValidationError

from app.data_base.db_helper.core import get_async_session_dependency
from app.client_session import get_async_client_session_dependency
from app.routes.check_signature import signature_verification_dependency
from app.routes.webhook.models.payload import WebHookPayload
from app.settings import Settings

log = logging.getLogger(__name__)

settings = Settings()

webhook_bp = APIRouter()

WEBHOOK_VERIFY_TOKEN = settings.webhook_verify_token


@webhook_bp.get("/webhook")
async def verify(request: Request) -> Response:
    """Verifies if ACCESS TOKEN matches the one from facebook endpoint.
    Required for registration of webhook."""

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
            log.info("Successfully verified web hook token!")

            return Response(challenge, media_type="text/plain", status_code=200)

        else:
            log.error("Verification failed")

            return JSONResponse(
                {"status": "error", "message": "Verification failed"}, status_code=403
            )

    log.error("Missing parameters")

    return JSONResponse(
        {"status": "error", "message": "Missing parameters"}, status_code=400
    )


@webhook_bp.post("/webhook", response_model=None)
async def webhook_post(
    request: Request,
    background_tasks: BackgroundTasks,
    db_session: Annotated[AsyncSession, Depends(get_async_session_dependency)],
    client_session: Annotated[
        ClientSession, Depends(get_async_client_session_dependency)
    ],
    signature_valid: Annotated[None, Depends(signature_verification_dependency)],
) -> Response:
    """Runs whenever we get a post request from the webhook."""
    try:
        raw: bytes = await request.body()
        
        payload = WebHookPayload.model_validate_json(raw)

        log.info("Offloading to background task")
        background_tasks.add_task(
            payload.handle,
            db_session,  # Since we will need to access the Data Base
            client_session,  # For asynchronous requests
        )  # Here i just pass the functions we define for each payload type

        return JSONResponse(
            {"status": "success"}, status_code=200
        )  # Always good to send this back, in order to not get blocked, just say you got the response
    # TODO: proper fault to facebook for bad webhooks
    except ValidationError as e:
        log.exception(f"[Malformed data]: {e}")
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)
    except ValueError as e:
        log.exception(f"[Malformed json]: {e}")
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)
    except Exception as e:
        log.exception(f"[Unexpected error]: {e}")
        return JSONResponse({"error": "Internal Server Error"}, status_code=500)
