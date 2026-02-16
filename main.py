import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from bot.config import config
from aiogram.fsm.storage.memory import MemoryStorage

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    # Initialize database for SQLite (skip for PostgreSQL as migrations handle it)
    if "sqlite" in config.database_url:
        from bot.database.session import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("SQLite database initialized")

    # Middleware
    from bot.middlewares.db import DbSessionMiddleware
    dp.update.middleware(DbSessionMiddleware())

    # Router
    from bot.handlers import main_router
    dp.include_router(main_router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
