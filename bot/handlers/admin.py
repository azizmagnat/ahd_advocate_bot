from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import logging

from bot.states.admin import AnswerQuestion, MessageUser
from bot.keyboards import admin as admin_kb
from bot.keyboards import common as common_kb
from bot.services.payment_service import PaymentService
from bot.services.question_service import QuestionService
from bot.middlewares.auth import AdminMiddleware
from bot.database.models import Question, Payment, User

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

@router.message(F.text == "💳 Kutilayotgan to'lovlar")
async def view_payments(message: types.Message, session: AsyncSession):
    payments = await PaymentService.get_pending_payments(session)
    if not payments:
        await message.answer("Hozircha kutilayotgan to'lovlar yo'q.")
        return
    
    for p in payments:
        # Get user_id from question
        question = await QuestionService.get_question(session, p.question_id)
        user_telegram_id = None
        if question:
            res = await session.execute(select(User).where(User.id == question.user_id))
            user = res.scalars().first()
            if user:
                user_telegram_id = user.telegram_id
        
        await message.answer_photo(
            photo=p.proof_file_id,
            caption=f"💳 <b>To'lov #{p.id}</b>\nSavol ID: #{p.question_id}\nSuma: {p.amount} so'm",
            reply_markup=admin_kb.get_payment_action_kb(p.id, user_telegram_id or 0),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("confirm_payment:"))
async def confirm_payment(callback: types.CallbackQuery, session: AsyncSession, bot: Bot):
    payment_id = int(callback.data.split(":")[1])
    payment = await PaymentService.confirm_payment(session, payment_id)
    if payment:
        await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ <b>TASDIQLANDI</b>", parse_mode="HTML")
        await callback.answer("To'lov tasdiqlandi")
        
        # Notify user
        question = await QuestionService.get_question(session, payment.question_id)
        if question:
            try:
                # Find user telegram id
                res = await session.execute(select(User).where(User.id == question.user_id))
                user = res.scalars().first()
                if user:
                    await bot.send_message(
                        user.telegram_id, 
                        f"✅ Savol #{question.id} uchun to'lovingiz tasdiqlandi! "
                        "Tez orada advokat javob yo'llaydi."
                    )
            except Exception:
                pass
    else:
        await callback.answer("Xatolik yuz berdi")

@router.callback_query(F.data.startswith("reject_payment:"))
async def reject_payment(callback: types.CallbackQuery, session: AsyncSession):
    payment_id = int(callback.data.split(":")[1])
    await PaymentService.reject_payment(session, payment_id)
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n❌ <b>RAD ETILDI</b>", parse_mode="HTML")
    await callback.answer("To'lov rad etildi")

@router.message(F.text == "📩 To'langan savollar")
async def view_questions(message: types.Message, session: AsyncSession):
    questions = await QuestionService.get_questions_to_answer(session)
    if not questions:
        await message.answer("Javob berilishi kerak bo'lgan savollar yo'q.")
        return
    
    for q in questions:
        await message.answer(
            f"❓ <b>Savol #{q.id}</b>\n\n{q.text}",
            reply_markup=admin_kb.get_question_action_kb(q.id),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("answer_question:"))
async def start_answering(callback: types.CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split(":")[1])
    await state.update_data(question_id=question_id)
    await state.set_state(AnswerQuestion.waiting_for_answer_text)
    await callback.message.answer(f"✍️ Savol #{question_id} uchun javob yozing:", reply_markup=common_kb.get_cancel_kb())
    await callback.answer()

@router.message(AnswerQuestion.waiting_for_answer_text)
async def submit_answer(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()
    question_id = data.get("question_id")
    
    question = await QuestionService.submit_answer(session, question_id, message.text)
    
    await state.clear()
    await message.answer(f"✅ Savol #{question_id} uchun javob yuborildi!", reply_markup=admin_kb.get_admin_main_kb())
    
    # Notify user
    try:
        res = await session.execute(select(User).where(User.id == question.user_id))
        user = res.scalars().first()
        if user:
            await bot.send_message(
                user.telegram_id,
                f"📩 <b>Savolingizga javob keldi (ID #{question_id}):</b>\n\n{message.text}",
                parse_mode="HTML"
            )
    except Exception:
        pass
    
    # Archive to group (if configured)
    from bot.config import config
    if config.archive_group_id:
        try:
            archive_message = (
                f"📚 <b>Yangi Savol-Javob Arxivi</b>\n\n"
                f"🆔 Murojaat: #{question_id}\n"
                f"📅 Sana: {question.created_at.strftime('%d.%m.%Y')}\n\n"
                f"❓ <b>Savol:</b>\n{question.text}\n\n"
                f"💬 <b>Javob:</b>\n{message.text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━"
            )
            await bot.send_message(
                config.archive_group_id,
                archive_message,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Failed to send to archive group: {e}")

# Admin Messaging System
@router.callback_query(F.data.startswith("message_user:"))
async def initiate_message_user(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    payment_id = int(parts[1])
    user_telegram_id = int(parts[2])
    
    if user_telegram_id == 0:
        await callback.answer("Foydalanuvchi topilmadi", show_alert=True)
        return
    
    await state.update_data(target_user_id=user_telegram_id, payment_id=payment_id)
    await state.set_state(MessageUser.waiting_for_message_text)
    await callback.message.answer(
        "✉️ Foydalanuvchiga yuboriladigan xabarni yozing:\n\n"
        "<i>Bekor qilish uchun /cancel buyrug'ini yuboring.</i>",
        reply_markup=common_kb.get_cancel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(MessageUser.waiting_for_message_text)
async def send_message_to_user(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("target_user_id")
    payment_id = data.get("payment_id")
    
    try:
        await bot.send_message(
            user_id,
            f"📨 <b>Admin xabari:</b>\n\n{message.text}",
            parse_mode="HTML"
        )
        await message.answer(
            "✅ Xabar muvaffaqiyatli yuborildi!",
            reply_markup=admin_kb.get_admin_main_kb()
        )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: Xabarni yuborib bo'lmadi.\n\n<code>{str(e)}</code>",
            reply_markup=admin_kb.get_admin_main_kb(),
            parse_mode="HTML"
        )
    
    await state.clear()

@router.message(F.text == "📊 Statistika")
async def view_stats(message: types.Message, session: AsyncSession):
    users_count = await session.execute(select(func.count(User.id)))
    questions_count = await session.execute(select(func.count(Question.id)))
    payments_sum = await session.execute(select(func.sum(Payment.amount)).where(Payment.status == "confirmed"))
    
    stats_text = (
        "📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar: {users_count.scalar()}\n"
        f"❓ Umumiy savollar: {questions_count.scalar()}\n"
        f"💵 Umumiy tushum: {payments_sum.scalar() or 0} so'm"
    )
    await message.answer(stats_text, parse_mode="HTML")
