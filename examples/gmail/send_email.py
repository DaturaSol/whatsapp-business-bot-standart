import os
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio

load_dotenv()
TESTER_EMAIL = os.getenv("TESTER_EMAIL")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

# Interesting to add
if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, TESTER_EMAIL]):
    missing = [
        name
        for name, val in {
            "SMTP_SERVER": SMTP_SERVER,
            "SMTP_PORT": SMTP_PORT,
            "SMTP_USER": SMTP_USER,
            "SMTP_PASSWORD": SMTP_PASSWORD,
            "TESTER_EMAIL": TESTER_EMAIL,
        }.items()
        if not val
    ]
    raise EnvironmentError(f"Missing SMTP environment variables: {', '.join(missing)}")
# 

try:
    SMTP_PORT = int(SMTP_PORT)

    CURRENT_DIR = os.getcwd()
    with open(os.path.join(CURRENT_DIR, "assets/examples/html/template.html")) as file:
        HTML_CONTENT = file.read()
except Exception as e:
    raise e


async def _send_email():
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = TESTER_EMAIL
    msg["Subject"] = "Testing Email"
    msg.attach(MIMEText(HTML_CONTENT, "html"))
    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            use_tls=True,  # IF port is 465 SSL
            # start_tls=True, # if port is 587 STARTTLS
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            timeout=60,
        )
    except Exception as e:
        raise e


async def main():
    await _send_email()


if __name__ == "__main__":
    asyncio.run(main())
