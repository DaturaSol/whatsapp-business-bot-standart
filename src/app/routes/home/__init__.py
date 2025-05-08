"""Just a silly Home page to make sure it is wokring"""

from fastapi import APIRouter, Response

home_bp = APIRouter()


@home_bp.get("/")
async def home_route():
    return Response("Congratulations, i think it is working!", media_type="text/plain")
