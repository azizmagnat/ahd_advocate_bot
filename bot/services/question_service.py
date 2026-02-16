from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import Question, QuestionStatus, User, UserRole

class QuestionService:
    @staticmethod
    async def create_new_question(session: AsyncSession, user_id: int, telegram_id: int, text: str) -> Question:
        # Ensure user exists
        user = await crud.get_user_by_telegram_id(session, telegram_id)
        if not user:
            user = await crud.create_user(session, telegram_id, UserRole.USER)
        
        return await crud.create_question(session, user.id, text)

    @staticmethod
    async def get_user_history(session: AsyncSession, telegram_id: int):
        user = await crud.get_user_by_telegram_id(session, telegram_id)
        if not user:
            return []
        return await crud.get_user_questions(session, user.id)

    @staticmethod
    async def get_questions_to_answer(session: AsyncSession):
        return await crud.get_unanswered_questions(session)

    @staticmethod
    async def submit_answer(session: AsyncSession, question_id: int, answer_text: str):
        return await crud.update_question_answer(session, question_id, answer_text)

    @staticmethod
    async def get_question(session: AsyncSession, question_id: int):
        return await crud.get_question_by_id(session, question_id)
