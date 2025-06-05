"""Very basic very primitive i would use this at the end"""

import json
import aiohttp
import asyncio
from typing import Any
from logging import getLogger
from aiohttp import ClientSession, ClientTimeout, ClientResponse

from app.settings import Settings

log = getLogger(__name__)


setting = Settings()

GEMINI_API_KEY = setting.gemini_api_key


async def _make_gemini_request(
    client_session: ClientSession, model_name: str, prompt: str, timeout_seconds: int
) -> tuple[int, dict | str | None]:
    """
    Makes the API request and returns status code and parsed body (JSON or error text).
    Handles reading the response body within the context manager.
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not configured properly.")
        return (
            0,
            "API Key not configured",
        )  # Using 0 as a special status for internal error

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data: dict[str, Any] = {"contents": [{"parts": [{"text": prompt}]}]}
    data["safetySettings"] = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]
    # data["generationConfig"] = {"temperature": 0.7}

    log.debug(
        f"Requesting Gemini model {model_name} with prompt (first 30 chars): {prompt[:30]}..."
    )
    async with client_session.post(
        url=url,
        headers=headers,
        json=data,
        timeout=ClientTimeout(total=timeout_seconds),
    ) as response:
        status = response.status
        try:
            if status == 200:
                json_payload = await response.json()
                return status, json_payload
            else:
                error_text = await response.text()
                return status, error_text
        except (aiohttp.ContentTypeError, json.JSONDecodeError) as e:
            # This might happen if the server returns 200 OK but with non-JSON content (unlikely for this API)
            # or if an error response (e.g. 400) returns non-JSON (also unlikely but good to cover)
            error_text_after_parse_fail = (
                await response.text()
            )  # Attempt to get raw text
            log.error(
                f"Model {model_name} (HTTP {status}): JSON parsing error '{e}'. Body: {error_text_after_parse_fail[:200]}"
            )
            return status, f"JSON parsing error: {error_text_after_parse_fail[:200]}"
        except Exception as e:  # Catch-all for other issues during response reading
            log.exception(
                f"Model {model_name} (HTTP {status}): Unexpected error reading response body: {e}"
            )
            return status, f"Unexpected error reading response: {str(e)}"


async def get_ai_response(
    client_session: ClientSession,
    prompt: str,
    timeout_seconds: int = 60,  # Default timeout
) -> str | None:
    # Consider making models_to_try a parameter or loading from settings for flexibility
    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]  # Example models

    for model_name in models_to_try:
        log.debug(f"Attempting model: {model_name}")
        try:
            status_code, response_data = await _make_gemini_request(
                client_session=client_session,
                model_name=model_name,
                prompt=prompt,
                timeout_seconds=timeout_seconds,
            )

            if status_code == 0:  # Special case for API key not configured in helper
                log.error(
                    f"API Key error from _make_gemini_request: {response_data}. Stopping."
                )
                return None

            if status_code == 200:
                if not isinstance(response_data, dict):
                    log.error(
                        (
                            f"Model {model_name} returned 200 but data was"
                            f"not a dict: {str(response_data)[:200]}. Trying next model."
                        )
                    )
                    continue

                json_response = (
                    response_data  # response_data is already the parsed JSON
                )

                # Check for prompt-level blocking (though less common if safetySettings are tuned)
                prompt_feedback = json_response.get("promptFeedback")
                if prompt_feedback and prompt_feedback.get("blockReason"):
                    log.warning(
                        f"Model {model_name}: Prompt blocked (Reason: {prompt_feedback.get('blockReason')}, "
                        f"SafetyRatings: {prompt_feedback.get('safetyRatings')}). Trying next model."
                    )
                    continue

                candidates = json_response.get("candidates")
                if candidates:
                    candidate = candidates[0]
                    finish_reason = candidate.get("finishReason")

                    if finish_reason == "SAFETY":
                        log.warning(
                            (
                                f"Model {model_name}: Generated content blocked due to SAFETY. "
                                f"Details: {candidate.get('safetyRatings')}. Trying next model."
                            )
                        )
                        continue

                    if finish_reason == "STOP":
                        content = candidate.get("content")
                        if (
                            content
                            and content.get("parts")
                            and content["parts"][0].get("text")
                        ):
                            text_response = content["parts"][0]["text"]
                            log.debug(f"Success with model: {model_name}")
                            return text_response
                        else:
                            log.warning(
                                (
                                    f"Model {model_name}: No text content in successful response "
                                    f"(Finish reason: {finish_reason}). Data: {str(json_response)[:200]}. Trying next."
                                )
                            )
                            continue
                    else:  # Other finish reasons like MAX_TOKENS, RECITATION, OTHER
                        log.warning(
                            (
                                f"Model {model_name}: Finished with reason '{finish_reason}'."
                                f"Response: {str(json_response)[:200]}. Trying next model."
                            )
                        )
                        continue  # Or handle MAX_TOKENS by returning partial if available
                else:  # No candidates
                    log.warning(
                        (
                            f"Model {model_name}: No candidates in successful response. "
                            f"Response: {str(json_response)[:200]}. Trying next model."
                        )
                    )
                    continue

            # Handle errors that suggest the model is busy, unavailable, or a transient server issue
            elif status_code in [400, 404, 500, 503]:
                error_body = str(
                    response_data
                )  # response_data is the error text from _make_gemini_request
                log.warning(  # Changed to warning as we are trying next model
                    f"Model {model_name} failed (HTTP {status_code}): {error_body[:200]}. Trying next model."
                )
                continue

            elif status_code == 429:  # Rate limit
                error_body = str(response_data)
                log.error(
                    f"Rate limited (429) with model {model_name}: {error_body[:200]}. Stopping all attempts."
                )
                return None

            elif status_code == 401:  # Unauthorized
                error_body = str(response_data)
                log.error(
                    f"Unauthorized (401) for model {model_name}: {error_body[:200]}. Check API Key. Stopping."
                )
                return None
            elif status_code == 403:  # Forbidden
                error_body = str(response_data)
                log.error(
                    f"Forbidden (403) for model {model_name}: {error_body[:200]}. Check API Key permissions. Stopping."
                )
                return None
            else:  # Other critical/unhandled HTTP errors
                error_body = str(response_data)
                log.error(
                    f"Unhandled HTTP error {status_code} with model {model_name}: {error_body[:200]}. Stopping attempts."
                )
                return None  # Or optionally 'continue' if you want to try other models even for unknown HTTP errors

        except asyncio.TimeoutError:
            log.warning(  # Changed to warning
                f"Model {model_name} timed out after {timeout_seconds}s. Trying next model."
            )
            continue
        except aiohttp.ClientConnectionError as e:
            log.warning(
                f"Connection error with model {model_name}: {e}. Trying next model."
            )  # Changed to warning
            continue
        except (
            aiohttp.ClientError
        ) as e:  # Catch other aiohttp client errors (e.g., payload, etc.)
            log.warning(
                f"AIOHTTP client error with model {model_name}: {e}. Trying next model."  # Changed to warning
            )
            continue
        # Removed json.JSONDecodeError here as _make_gemini_request handles it
        except (
            Exception
        ) as e:  # Catch-all for any other unexpected error during THIS model's attempt
            log.exception(  # Keep as exception for unexpected issues
                f"Unexpected error while processing model {model_name}: {e}. Trying next model."
            )
            continue

    log.error(
        f"All models in list {models_to_try} failed for the prompt (first 30 chars): '{prompt[:30]}...'."
    )
    return None
