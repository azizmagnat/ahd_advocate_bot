from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bot.database.models import User, Question, Payment, UserRole, QuestionStatus, PaymentStatus
from typing import Optional, List

# User CRUD
async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user(session: AsyncSession, telegram_id: int, role: UserRole = UserRole.USER) -> User:
    user = User(telegram_id=telegram_id, role=role)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Question CRUD
async def create_question(session: AsyncSession, user_id: int, text: str) -> Question:
    question = Question(user_id=user_id, text=text)
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question

async def get_question_by_id(session: AsyncSession, question_id: int) -> Optional[Question]:
    result = await session.execute(select(Question).where(Question.id == question_id))
    return result.scalars().first()

async def get_user_questions(session: AsyncSession, user_id: int) -> List[Question]:
    result = await session.execute(select(Question).where(Question.user_id == user_id).order_by(Question.created_at.desc()))
    return result.scalars().all()

async def get_unanswered_questions(session: AsyncSession) -> List[Question]:
    # Pending payment or paid but not answered? 
    # Usually admin wants to see paid questions to answer
    result = await session.execute(select(Question).where(Question.status == QuestionStatus.PAID).order_by(Question.created_at.asc()))
    return result.scalars().all()

async def update_question_answer(session: AsyncSession, question_id: int, answer: str) -> Optional[Question]:
    question = await get_question_by_id(session, question_id)
    if question:
        question.answer = answer
        question.status = QuestionStatus.ANSWERED
        await session.commit()
        await session.refresh(question)
    return question

async def update_question_status(session: AsyncSession, question_id: int, status: QuestionStatus) -> Optional[Question]:
    question = await get_question_by_id(session, question_id)
    if question:
        question.status = status
        await session.commit()
        await session.refresh(question)
    return question

# Payment CRUD
async def create_payment(session: AsyncSession, question_id: int, amount: float, proof_file_id: str) -> Payment:
    payment = Payment(question_id=question_id, amount=amount, proof_file_id=proof_file_id)
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment

async def get_payment_by_id(session: AsyncSession, payment_id: int) -> Optional[Payment]:
    result = await session.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalars().first()

async def get_pending_payments(session: AsyncSession) -> List[Payment]:
    result = await session.execute(select(Payment).where(Payment.status == PaymentStatus.PENDING).order_by(Payment.created_at.asc()))
    return result.scalars().all()

async def update_payment_status(session: AsyncSession, payment_id: int, status: PaymentStatus) -> Optional[Payment]:
    payment = await get_payment_by_id(session, payment_id)
    if payment:
        payment.status = status
        await session.commit()
        await session.refresh(payment)
    return payment
