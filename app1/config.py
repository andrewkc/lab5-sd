import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///champions.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MATCHES_API_URL = os.getenv("MATCHES_API_URL", "http://localhost:5000/api/mock/matches")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
