from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: int
    database_url: str
    archive_group_id: int | None = None  # Optional: Telegram group ID for Q&A archive
    
    # Click Payment (Test Mode)
    click_merchant_id: int | None = None
    click_service_id: int | None = None
    click_secret_key: SecretStr | None = None
    click_test_mode: bool = True
    
    # Payme Payment (Test Mode)
    payme_merchant_id: str | None = None
    payme_secret_key: SecretStr | None = None
    payme_test_mode: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

config = Settings()

# Fix for Railway/Heroku using postgres:// instead of postgresql+asyncpg://
if config.database_url:
    if config.database_url.startswith("postgres://"):
        config.database_url = config.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif config.database_url.startswith("postgresql://"):
        config.database_url = config.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

import logging
# Mask password for logs
masked_url = config.database_url.split("@")[-1] if "@" in config.database_url else "unknown"
logging.info(f"Database URL scheme fixed. Target host: {masked_url}")
