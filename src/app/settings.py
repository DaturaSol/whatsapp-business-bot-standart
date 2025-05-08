from environs import Env
from dataclasses import dataclass


env = Env()
env.read_env()


@dataclass(frozen=True)
class Settings:
    # [Ports]
    port = env.str("PORT")

    # [Gemini]
    gemini_api_key = env.str("GEMINI_API_KEY")

    # [Meta]
    api_version = env.str("API_VERSION")
    phone_number_id = env.str("PHONE_NUMBER_ID")
    access_token = env.str("ACCESS_TOKEN")
    app_secret = env.str("APP_SECRET")
    whatsapp_business_account_id = env.str("WHATSAPP_BUSINESS_ACCOUNT_ID")
    webhook_verify_token = env.str("WEBHOOK_VERIFY_TOKEN")
    passphrase = env.str("PASSPHRASE")
    private_key = env.str("PRIVATE_KEY")
    public_key = env.str("PUBLIC_KEY")

    # [Gmail]
    smtp_user = env.str("SMTP_USER")
    smtp_password = env.str("SMTP_PASSWORD")
    smtp_server = env.str("SMTP_SERVER")
    smtp_port = env.str("SMTP_PORT")

    # [Sql]
    db_url = env.str("DB_URl")

    # [Etc]
    tester_number = env.str("TESTER_NUMBER")
    tester_email = env.str("TESTER_EMAIL")
