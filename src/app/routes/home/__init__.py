"""Just a silly Home page to make sure it is wokring"""

from fastapi import APIRouter, Response

from app.settings import Settings

home_bp = APIRouter()

settings = Settings()

a = {
    "settings.webhook_verify_token": settings.webhook_verify_token,
    "is_1234": settings.webhook_verify_token == "1234",
    "account_id": settings.whatsapp_business_account_id == "653355860631136",
    "id": settings.whatsapp_business_account_id
}


@home_bp.get("/")
async def home_route():
    return Response(f"Congratulations, i think it is working!\n{a}", media_type="text/plain")
