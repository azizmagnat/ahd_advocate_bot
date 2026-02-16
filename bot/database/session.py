from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.config import config
import ssl

# Configure connect_args for asyncpg if using Postgres
connect_args = {}
if "postgresql" in config.database_url:
    # Most cloud providers (Railway, Heroku) require SSL.
    # We might need to bypass hostname verification for self-signed certs if issues arise,
    # or just trust the system CA.
    # For robust production, creating an SSL context is safer.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    config.database_url, 
    echo=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
