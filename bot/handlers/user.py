from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.user import AskQuestion, SendProof
from bot.keyboards import user as user_kb
from bot.keyboards import common as common_kb
from bot.services.question_service import QuestionService
from bot.services.payment_service import PaymentService
from bot.config import config
from bot.keyboards.admin import get_payment_action_kb

router = Router()

@router.message(F.text == "Ask Question")
async def ask_question_start(message: types.Message, state: FSMContext):
    await state.set_state(AskQuestion.waiting_for_question_text)
    await message.answer("Please type your question:", reply_markup=common_kb.get_cancel_kb())

@router.message(AskQuestion.waiting_for_question_text)
async def process_question_text(message: types.Message, state: FSMContext, session: AsyncSession):
    questions_text = message.text
    question = await QuestionService.create_new_question(session, message.from_user.id, message.from_user.id, questions_text)
    
    await state.clear()
    await message.answer(
        f"Question #{question.id} received!\n"
        f"Please transfer 50,000 UZS to 8600 0000 0000 0000 (John Doe)\n"
        f"Then click 'I have paid' below.",
        reply_markup=user_kb.get_pay_command_kb(question.id)
    )

@router.callback_query(F.data.startswith("pay:"))
async def process_pay_click(callback: types.CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split(":")[1])
    await state.update_data(question_id=question_id)
    await state.set_state(SendProof.waiting_for_screenshot)
    await callback.message.answer("Please send a screenshot of the payment receipt.", reply_markup=common_kb.get_cancel_kb())
    await callback.answer()

@router.message(SendProof.waiting_for_screenshot, F.photo)
async def process_proof_photo(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    question_id = data.get("question_id")
    photo_id = message.photo[-1].file_id # Get largest photo
    
    # Save payment
    payment = await PaymentService.submit_payment(session, question_id, 50000.0, photo_id) # Using dummy amount
    
    await state.clear()
    await message.answer("Payment proof received! Wait for admin confirmation.", reply_markup=user_kb.get_main_kb())
    
    # Notify Admin
    try:
        await bot.send_photo(
            chat_id=config.admin_id,
            photo=photo_id,
            caption=f"New Payment for Question #{question_id}\nAmount: 50,000",
            reply_markup=get_payment_action_kb(payment.id)
        )
    except Exception as e:
        # Log error or something
        pass

@router.message(F.text == "My Questions")
async def view_my_questions(message: types.Message, session: AsyncSession):
    questions = await QuestionService.get_user_history(session, message.from_user.id)
    if not questions:
        await message.answer("You have no questions yet.")
        return
    
    response = "Your Questions:\n\n"
    for q in questions:
        status_emoji = "⏳" if q.status == "pending" else "✅" if q.status == "paid" else "📩"
        response += f"#{q.id} [{q.status.upper()}] {q.text[:20]}...\nAnswer: {q.answer or 'Waiting...'}\n\n"
    
    await message.answer(response)
