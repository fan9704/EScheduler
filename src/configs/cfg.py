from os import environ
from dotenv import load_dotenv

load_dotenv()

APPLICATION_PORT = 8000

IS_TEST = bool(environ.get("API_TEST"))
IS_CONTAINER = environ.get("IS_CONTAINER",False)
SECRET_KEY = environ.get("SECRET_KEY")
API_ENDPOINT = environ.get("API_ENDPOINT", "http://localhost:8000")
GENERATE_DB_SCHEMA = environ.get("GENERATE_DB_SCHEMA", True)
ALLOW_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]

TZ = environ.get("TZ", "Asia/Taipei")