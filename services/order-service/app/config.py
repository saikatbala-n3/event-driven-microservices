import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Service
    SERVICE_NAME: str = "order-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@postgres_local:5432/order_db",
    )

    # RabbitMQ
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

    # Jaeger
    JAEGER_ENDPOINT: str = os.getenv("JAEGER_ENDPOINT", "http://jaeger:4318/v1/traces")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
