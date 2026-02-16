import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.database.models import Base, User, Question, Payment, UserRole, QuestionStatus
from bot.services.question_service import QuestionService
from bot.services.payment_service import PaymentService
from bot.config import config

# Use in-memory SQLite for testing or a test DB
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user_and_question(session):
    telegram_id = 123456789
    text = "How do I reset my password?"
    
    question = await QuestionService.create_new_question(session, telegram_id, telegram_id, text)
    assert question.id is not None
    assert question.text == text
    assert question.status == QuestionStatus.PENDING

@pytest.mark.asyncio
async def test_payment_flow(session):
    telegram_id = 987654321
    question = await QuestionService.create_new_question(session, telegram_id, telegram_id, "Payment Test")
    
    payment = await PaymentService.submit_payment(session, question.id, 50000.0, "file_id_123")
    assert payment.id is not None
    assert payment.status == "pending"
    
    # Confirm
    confirmed = await PaymentService.confirm_payment(session, payment.id)
    assert confirmed.status == "confirmed"
    
    # Check question status
    await session.refresh(question)
    assert question.status == QuestionStatus.PAID
