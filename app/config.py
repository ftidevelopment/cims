import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(
    BASE_DIR / ".env"
)


class Config:

    # ==========================================
    # Application
    # ==========================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    APP_NAME = os.getenv("APP_NAME")

    APP_ENV = os.getenv("APP_ENV")

    APP_DEBUG = (
        os.getenv("APP_DEBUG") == "True"
    )

    # ==========================================
    # Upload
    # ==========================================

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "static/uploads",
    )

    MAX_CONTENT_LENGTH = int(
        os.getenv(
            "MAX_CONTENT_LENGTH",
            "10485760",
        )
    )

    # ==========================================
    # Email
    # ==========================================

    MAIL_PROVIDER = os.getenv(
        "MAIL_PROVIDER",
        "gmail",
    )

    MAIL_SERVER = os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com",
    )

    MAIL_PORT = int(
        os.getenv(
            "MAIL_PORT",
            "587",
        )
    )

    MAIL_USERNAME = os.getenv(
        "MAIL_USERNAME",
    )

    MAIL_PASSWORD = os.getenv(
        "MAIL_PASSWORD",
    )

    MAIL_USE_TLS = (
        os.getenv(
            "MAIL_USE_TLS",
            "true",
        ).lower()
        == "true"
    )

    # ==========================================
    # Notification
    # ==========================================

    NOTIFICATION_TEST_EMAIL = os.getenv(
        "NOTIFICATION_TEST_EMAIL"
    )

    LINE_CHANNEL_ACCESS_TOKEN = os.getenv(
        "LINE_CHANNEL_ACCESS_TOKEN"
    )

    LINE_CHANNEL_SECRET = os.getenv(
        "LINE_CHANNEL_SECRET"
    )

    LINE_LOGIN_CHANNEL_ID = os.getenv(
        "LINE_LOGIN_CHANNEL_ID"
    )

    LINE_LIFF_ID = os.getenv(
        "LINE_LIFF_ID"
    )

    # ==========================================
    # Celery / Redis
    # ==========================================

    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0",
    )

    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1",
    )

    # ==========================================
    # Logging
    # ==========================================

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL"
    )

    LOG_FOLDER = os.getenv(
        "LOG_FOLDER"
    )

    # ==========================================
    # Database
    # ==========================================

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False