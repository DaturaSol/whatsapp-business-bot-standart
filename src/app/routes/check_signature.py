"""Module responsible to check if incoming payload is indeed from Meta."""

from fastapi import HTTPException, Request, status
import hashlib
import hmac
import logging
import os

log = logging.getLogger(__name__)

try:
    APP_SECRET = os.environ.get("APP_SECRET")

    assert APP_SECRET is not None

except AssertionError:
    log.error("No APP SECRET found")
    raise

except Exception as e:
    log.exception(f"An unexpected error occurred during setup: {e}")
    raise


log.info("APP Secret properly loaded")


def validate_signature(payload: str, signature: str) -> bool:
    """Validate the incoming payload's signature"""

    expected_signature = hmac.new(
        bytes(APP_SECRET, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


async def signature_verification_dependency(request: Request):
    """FastAPI dependency to verify the signature of incoming requests.
    Raises HTTPException if signature is invalid."""

    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        log.warning("(BAD REQUEST) Missing X-Hub-Signature-256 header")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Hub-Signature-256 header",
        )

    if signature.startswith("sha256="):
        signature = signature[7:]

    else:
        log.warning("(BAD REQUEST) Invalid signature format")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature format",
        )

    request_body = await request.body()  # Get request body as bytes
    payload = request_body.decode("utf-8")

    if not validate_signature(payload, signature):
        log.warning("(FORBIDEN) Invalid signature")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature"
        )
