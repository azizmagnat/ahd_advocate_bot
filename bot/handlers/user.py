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

@router.message(F.text == "❓ Savol berish")
async def ask_question_start(message: types.Message, state: FSMContext):
    await state.set_state(AskQuestion.waiting_for_question_text)
    await message.answer(
        "<b>Savolingizni yozing:</b>\n\n"
        "Iltimos, vaziyatni batafsil tushuntiring. Savolingiz qanchalik aniq bo'lsa, "
        "javob ham shunchalik sifatli bo'ladi.",
        reply_markup=common_kb.get_cancel_kb(),
        parse_mode="HTML"
    )

@router.message(AskQuestion.waiting_for_question_text)
async def process_question_text(message: types.Message, state: FSMContext, session: AsyncSession):
    if not message.text or len(message.text) < 10:
        await message.answer("Savol juda qisqa. Iltimos, batafsilroq yozing.")
        return

    question = await QuestionService.create_new_question(session, message.from_user.id, message.from_user.id, message.text)
    
    await state.clear()
    payment_details = (
        f"📋 <b>Sizning savolingiz #{question.id} raqami bilan qabul qilindi.</b>\n\n"
        "Xizmat narxi: <b>50,000 so'm</b>\n\n"
        "<b>To'lov ma'lumotlari:</b>\n"
        "💳 Karta raqami: <code>8600 0000 0000 0000</code>\n"
        "👤 Qabul qiluvchi: <b>Palonchi Pistonchiyev</b>\n\n"
        "To'lovni amalga oshirgach, pastdagi tugmani bosing va to'lov chekini (screenshot) yuboring."
    )
    await message.answer(payment_details, reply_markup=user_kb.get_pay_command_kb(question.id), parse_mode="HTML")

@router.callback_query(F.data.startswith("pay:"))
async def process_pay_click(callback: types.CallbackQuery, state: FSMContext):
    question_id = int(callback.data.split(":")[1])
    await state.update_data(question_id=question_id)
    await state.set_state(SendProof.waiting_for_screenshot)
    await callback.message.answer(
        "📸 <b>To'lov chekini (rasmda) yuboring.</b>\n\n"
        "Chekda to'lov vaqti va summasi aniq ko'rinishi kerak.",
        reply_markup=common_kb.get_cancel_kb(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(SendProof.waiting_for_screenshot, F.photo)
async def process_proof_photo(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await bot.send_chat_action(message.chat.id, "upload_photo")
    data = await state.get_data()
    question_id = data.get("question_id")
    photo_id = message.photo[-1].file_id
    
    payment = await PaymentService.submit_payment(session, question_id, 50000.0, photo_id)
    
    await state.clear()
    await message.answer(
        "✅ <b>Rahmat! To'lov cheki qabul qilindi.</b>\n\n"
        "Admin to'lovni tasdiqlagach, savolingizga javob yo'llanadi. "
        "Holatni '📜 Mening savollarim' bo'limida kuzatishingiz mumkin.",
        reply_markup=user_kb.get_main_kb(),
        parse_mode="HTML"
    )
    
    # Notify Admin
    try:
        await bot.send_photo(
            chat_id=config.admin_id,
            photo=photo_id,
            caption=(
                f"🆕 <b>Yangi to'lov!</b>\n\n"
                f"Savol ID: #{question_id}\n"
                f"Mijoz: {message.from_user.full_name} (@{message.from_user.username or 'yo-q'})\n"
                f"Suma: 50,000 so'm"
            ),
            reply_markup=get_payment_action_kb(payment.id),
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.message(SendProof.waiting_for_screenshot)
async def process_proof_wrong_type(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekini <b>rasm ko'rinishida</b> yuboring.")


@router.message(F.text == "📜 Mening savollarim")
async def view_my_questions(message: types.Message, session: AsyncSession):
    questions = await QuestionService.get_user_history(session, message.from_user.id)
    if not questions:
        await message.answer("Sizda hali savollar yo'q.")
        return
    
    response = "📝 <b>Sizning savollaringiz:</b>\n" + ("—" * 15) + "\n\n"
    for q in questions:
        status_map = {
            "pending": "⏳ To'lov kutilmoqda",
            "paid": "🆗 To'langan / Javob kutilyapti",
            "answered": "✅ Javob berilgan"
        }
        status_text = status_map.get(q.status, q.status)
        
        response += f"🆔 Savol #{q.id}\n"
        response += f"📊 Holati: <b>{status_text}</b>\n"
        response += f"❓ Savol: <i>{q.text[:100]}{'...' if len(q.text) > 100 else ''}</i>\n"
        if q.answer:
            response += f"📩 <b>Javob:</b> {q.answer}\n"
        response += ("—" * 15) + "\n\n"
    
    await message.answer(response, parse_mode="HTML")

@router.message(F.text == "📞 Bog'lanish")
async def contact_us(message: types.Message):
    await message.answer(
        "<b>Biz bilan bog'lanish:</b>\n\n"
        "👨‍⚖️ Advokat: Palonchi Pistonchiyev\n"
        "📞 Telefon: +998 90 123 45 67\n"
        "📍 Manzil: Toshkent sh., Chilonzor tumani, 5-mavze.\n"
        "📧 Telegram: @advokat_admin",
        parse_mode="HTML"
    )
