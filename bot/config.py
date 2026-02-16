from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: int
    database_url: str

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
