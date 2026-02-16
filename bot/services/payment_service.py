from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import crud
from bot.database.models import Payment, PaymentStatus, QuestionStatus

class PaymentService:
    @staticmethod
    async def submit_payment(session: AsyncSession, question_id: int, amount: float, proof_file_id: str) -> Payment:
        return await crud.create_payment(session, question_id, amount, proof_file_id)
    
    @staticmethod
    async def create_online_payment(session: AsyncSession, question_id: int, amount: float, 
                                   payment_method: str, invoice_id: str, payment_url: str) -> Payment:
        """Create payment record for online payment (Click/Payme)"""
        return await crud.create_online_payment(
            session=session,
            question_id=question_id,
            amount=amount,
            payment_method=payment_method,
            invoice_id=invoice_id,
            payment_url=payment_url
        )

    @staticmethod
    async def get_pending_payments(session: AsyncSession):
        return await crud.get_pending_payments(session)

    @staticmethod
    async def confirm_payment(session: AsyncSession, payment_id: int):
        payment = await crud.update_payment_status(session, payment_id, PaymentStatus.CONFIRMED)
        if payment:
            # Update question status to PAID
            await crud.update_question_status(session, payment.question_id, QuestionStatus.PAID)
        return payment

    @staticmethod
    async def reject_payment(session: AsyncSession, payment_id: int):
        return await crud.update_payment_status(session, payment_id, PaymentStatus.REJECTED)
