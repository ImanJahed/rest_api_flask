import os

from dotenv import load_dotenv
from pathlib import Path
BASE_DIR2 = Path(__file__).resolve().parent
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    path = os.path.join(BASE_DIR, 'env', '.env-prod')
    load_dotenv(path)
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = os.getenv("SECRET_KEY")  # ==> for python-dotenv
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = "Stores REST API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")



