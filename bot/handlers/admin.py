from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.admin import AnswerQuestion
from bot.keyboards import admin as admin_kb
from bot.keyboards import common as common_kb # Assuming I might need cancel, but not essential
from bot.services.payment_service import PaymentService
from bot.services.question_service import QuestionService
from bot.middlewares.auth import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

@router.message(Command("admin"))
async def admin_start(message: types.Message):
    await message.answer("Admin Dashboard", reply_markup=admin_kb.get_admin_main_kb())

@router.message(F.text == "Pending Payments")
async def view_payments(message: types.Message, session: AsyncSession):
    start_msg = await message.answer("Loading payments...")
    payments = await PaymentService.get_pending_payments(session)
    if not payments:
        await start_msg.edit_text("No pending payments.")
        return
    
    await start_msg.delete()
    for p in payments:
        await message.answer_photo(
            photo=p.proof_file_id,
            caption=f"Payment #{p.id} for Question #{p.question_id}\nAmount: {p.amount}",
            reply_markup=admin_kb.get_payment_action_kb(p.id)
        )

@router.callback_query(F.data.startswith("confirm_payment:"))
async def confirm_payment(callback: types.CallbackQuery, session: AsyncSession):
    payment_id = int(callback.data.split(":")[1])
    payment = await PaymentService.confirm_payment(session, payment_id)
    if payment:
        await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n[CONFIRMED]")
        await callback.answer("Payment confirmed")
    else:
        await callback.answer("Payment not found or error")

@router.callback_query(F.data.startswith("reject_payment:"))
async def reject_payment(callback: types.CallbackQuery, session: AsyncSession):
    payment_id = int(callback.data.split(":")[1])
    await PaymentService.reject_payment(session, payment_id)
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n[REJECTED]")
    await callback.answer("Payment rejected")

@router.message(F.text == "Paid Questions")
async def view_questions(message: types.Message, session: AsyncSession):
    questions = await QuestionService.get_questions_to_answer(session)
    if not questions:
        await message.answer("No questions to answer.")
        return
    
    for q in questions:
        await message.answer(
            f"Question #{q.id}\n{q.text}",
            reply_markup=admin_kb.get_question_action_kb(q.id)
        )

@router.callback_query(F.data.startswith("answer_question:"))
async def start_answering(callback: types.CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split(":")[1])
    await state.update_data(question_id=question_id)
    await state.set_state(AnswerQuestion.waiting_for_answer_text)
    await callback.message.answer(f"Enter answer for Question #{question_id}:")
    await callback.answer()

@router.message(AnswerQuestion.waiting_for_answer_text)
async def submit_answer(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    question_id = data.get("question_id")
    answer_text = message.text
    
    question = await QuestionService.submit_answer(session, question_id, answer_text)
    
    await state.clear()
    await message.answer(f"Answer for Question #{question_id} submitted!")
