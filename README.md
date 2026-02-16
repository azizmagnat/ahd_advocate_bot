# Telegram Q&A Bot

Async Telegram Bot for Q&A with manual payment verification. Built with Aiogram 3, SQLAlchemy, and AsyncPG.

## Setup

1.  **Install Python**: Ensure Python 3.9+ is installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    - Rename `.env.example` to `.env` (already done if using provided .env).
    - Update `BOT_TOKEN` with your Telegram Bot Token.
    - Update `ADMIN_ID` with your Telegram User ID (you can find it in logs after running).
    - Database is pre-configured to use SQLite (`bot.db`). No installation needed.

## Database Migration

Run Alembic to create tables:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Bot

```bash
python main.py
```

## Running Tests

```bash
pytest tests/
```

## Project Structure

- `bot/handlers`: Command and message handlers.
- `bot/services`: Business logic (Question, Payment).
- `bot/database`: DB Models and CRUD.
- `bot/states`: FSM States.
- `bot/middlewares`: Auth and Session injection.
