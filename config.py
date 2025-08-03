import os
import secrets


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(16))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SMTP_SERVER = os.environ.get("SMTP_SERVER", "localhost")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 25))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "false").lower() == "true"

    CURRENCY_BY_LANG = {
        "pl": "PLN",
        "en": "USD",
        "ru": "USD",
        "uk": "PLN",
    }
