from os import environ
from dotenv import load_dotenv
from .smtp import get_smtp_settings

load_dotenv()

APPLICATION_PORT = 8000

IS_TEST = bool(environ.get("API_TEST"))
SECRET_KEY = environ.get("SECRET_KEY")
API_ENDPOINT = environ.get("API_ENDPOINT", "http://localhost:8000")
GENERATE_DB_SCHEMA = environ.get("GENERATE_DB_SCHEMA", True)
ALLOW_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]

TZ = environ.get("TZ", "Asia/Taipei")

# SMTP 設定
def get_settings():
    """獲取應用程式設定"""
    smtp_settings = get_smtp_settings()
    
    class Settings:
        SMTP_HOST = smtp_settings.host
        SMTP_PORT = smtp_settings.port
        SMTP_USERNAME = smtp_settings.username
        SMTP_PASSWORD = smtp_settings.password
        SMTP_USE_TLS = smtp_settings.use_tls
        SMTP_USE_SSL = smtp_settings.use_ssl
        DEFAULT_FROM_EMAIL = smtp_settings.default_from_email
        DEFAULT_FROM_NAME = smtp_settings.default_from_name
    
    return Settings()