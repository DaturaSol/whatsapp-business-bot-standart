from environs import Env
from dataclasses import dataclass


env = Env()
env.read_env()

# HACK: To be able to run on google cloud using the secret key manager
# It for some reason adds "\r\n" on the start of every .env variable. 
class Settings:
    # [Ports]
    # port = env.str("PORT")

    # [Gemini]
    gemini_api_key = env.str("GEMINI_API_KEY").replace("\r\n", "") 

    # [Meta]
    api_version = env.str("API_VERSION").replace("\r\n", "")
    phone_number_id = env.str("PHONE_NUMBER_ID").replace("\r\n", "")
    access_token = env.str("ACCESS_TOKEN").replace("\r\n", "")
    app_secret = env.str("APP_SECRET").replace("\r\n", "")
    whatsapp_business_account_id = env.str("WHATSAPP_BUSINESS_ACCOUNT_ID").replace("\r\n", "")
    webhook_verify_token = env.str("WEBHOOK_VERIFY_TOKEN").replace("\r\n", "")
    # passphrase = env.str("PASSPHRASE")
    # private_key = env.str("PRIVATE_KEY")
    # public_key = env.str("PUBLIC_KEY")

    # [Gmail]
    # smtp_user = env.str("SMTP_USER")
    # smtp_password = env.str("SMTP_PASSWORD")
    # smtp_server = env.str("SMTP_SERVER")
    # smtp_port = env.str("SMTP_PORT")

    # [Sql]
    db_url = env.str("DB_URl").replace("\r\n", "")

    # [Etc]
    # tester_number = env.str("TESTER_NUMBER")
    # tester_email = env.str("TESTER_EMAIL")
