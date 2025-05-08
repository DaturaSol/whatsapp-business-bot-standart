# %% 
import asyncio
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
# %%
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def _get_request(model: str, text: str) -> str | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    header = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": text}]}]}

    try:
        client_session = ClientSession()
        async with client_session.post(
            url=url, headers=header, json=data, timeout=10
        ) as response:
            json_response = await response.json()
            return json_response

    except Exception as e:
        raise e

    finally:
        await client_session.close()


async def main():
    response = await _get_request(model="gemini-2.0-flash", text="Say hello")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
