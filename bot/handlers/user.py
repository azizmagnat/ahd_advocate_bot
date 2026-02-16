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
        "⚖️ <b>Huquqiy maslahat so'rash</b>\n\n"
        "Huquqiy muammo yoki savolingizni batafsil bayon qiling.\n\n"
        "<i>💡 Ko'rsatma: Vaziyatni qanchalik aniq ifodalasangiz, "
        "professional maslahatingiz shunchalik samarali bo'ladi.</i>",
        reply_markup=common_kb.get_cancel_kb(),
        parse_mode="HTML"
    )

@router.message(AskQuestion.waiting_for_question_text)
async def process_question_text(message: types.Message, state: FSMContext, session: AsyncSession):
    if not message.text or len(message.text) < 10:
        await message.answer("Savol juda qisqa. Iltimos, batafsilroq yozing.")
        return

    # Create question in database
    question = await QuestionService.create_new_question(session, message.from_user.id, message.from_user.id, message.text)
    
    await state.clear()
    
    # AI Classification (if enabled)
    from bot.config import config
    
    # Debug logging
    import logging
    logging.info(f"AI enabled: {config.enable_ai_responses}, Has API key: {config.gemini_api_key is not None}")
    
    if config.enable_ai_responses and config.gemini_api_key:
        await message.answer("🤖 Savolingiz tahlil qilinmoqda...", parse_mode="HTML")
        
        from bot.ai import gemini_client, ai_responder
        
        # Classify question
        classification = await gemini_client.classify_question(message.text)
        
        logging.info(f"Classification result: {classification}")
        
        # Update question with AI classification
        from bot.database.crud import get_question_by_id
        question_obj = await get_question_by_id(session, question.id)
        if question_obj:
            question_obj.complexity = classification.get('complexity', 'medium')
            question_obj.ai_confidence = classification.get('confidence', 0.5)
            question_obj.category = classification.get('category', 'boshqa')
            await session.commit()
        
        complexity = classification.get('complexity')
        confidence = classification.get('confidence', 0)
        
        logging.info(f"Complexity: {complexity}, Confidence: {confidence}, Threshold: {config.ai_simple_threshold}")
        
        # Simple question - AI answers for free (lowered threshold to 0.6)
        if complexity == 'simple' and confidence >= 0.6:
            await message.answer("💡 Bu oddiy savol - bepul javob beramiz!", parse_mode="HTML")
            
            # Generate AI answer
            ai_answer = await ai_responder.generate_answer(
                message.text,
                classification.get('category', 'boshqa')
            )
            
            # Save AI answer
            if question_obj and ai_answer:
                question_obj.answer = ai_answer
                question_obj.status = "answered"
                question_obj.auto_answered = True
                await session.commit()
            
                # Send answer
                await message.answer(
                    f"🤖 <b>AI Javob:</b>\n\n{ai_answer}",
                    reply_markup=user_kb.get_main_kb(),
                    parse_mode="HTML"
                )
                return
            else:
                logging.error(f"AI answer generation failed")
        
        # Complex question - requires contract
        elif complexity == 'complex' and confidence >= config.ai_complex_threshold:
            if question_obj:
                question_obj.requires_human = True
                await session.commit()
            
            await message.answer(
                "⚠️ <b>Jiddiy huquqiy holat!</b>\n\n"
                "Bu ish uchun:\n"
                "✅ Professional advokat xizmati kerak\n"
                "✅ Shartnoma tuzish tavsiya etiladi\n\n"
                f"📋 Tahlil: {classification.get('reasoning', '')}\n\n"
                "📞 Sizga tez orada bog'lanamiz va batafsil maslahat beramiz.",
                reply_markup=user_kb.get_main_kb(),
                parse_mode="HTML"
            )
            return
    else:
        logging.info("AI responses disabled - proceeding to payment")
    
    # Medium question or AI disabled - require payment
    payment_details = (
        f"📋 <b>Murojaat #{question.id} ro'yxatga olindi</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚖️ <b>Konsultatsiya to'lovi:</b> 50,000 so'm\n\n"
        "<b>📤 To'lov ma'lumotlari:</b>\n"
        "💳 Karta: <code>8600 0000 0000 0000</code>\n"
        "👤 Qabul qiluvchi: <b>Azizbek To'ymurodov</b>\n\n"
        "<i>To'lovni amalga oshirgach, 'To'lov cheki' tugmasini bosib, "
        "to'lov tasdiqlovchi skrinshot yuboring.</i>"
    )
    await message.answer(payment_details, reply_markup=user_kb.get_pay_command_kb(question.id), parse_mode="HTML")

@router.callback_query(F.data.startswith("select_payment_method:"))
async def select_payment_method(callback: types.CallbackQuery):
    question_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "💳 <b>To'lov usulini tanlang:</b>\n\n"
        "💳 <b>Onlayn to'lov</b> - Darhol avtomatik tasdiqlanadi\n"
        "📸 <b>Chek yuborish</b> - Admin tomonidan tekshiriladi",
        reply_markup=user_kb.get_payment_method_kb(question_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("online_payment:"))
async def select_online_provider(callback: types.CallbackQuery):
    question_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "💳 <b>To'lov tizimini tanlang:</b>\n\n"
        "🔵 <b>Click</b> - Visa, Mastercard, Humo\n"
        "🟢 <b>Payme</b> - Barcha kartalar\n\n"
        "<i>⚠️ Test rejimda: API kalitlar kiritilganda real to'lovlar ishlay boshlaydi</i>",
        reply_markup=user_kb.get_online_provider_kb(question_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("manual_payment:"))
async def process_manual_payment(callback: types.CallbackQuery, state: FSMContext):
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

@router.callback_query(F.data.startswith("pay_click:"))
async def process_click_payment(callback: types.CallbackQuery, session: AsyncSession):
    question_id = int(callback.data.split(":")[1])
    
    from bot.payments.click import ClickPayment
    from bot.config import config
    
    # Initialize Click provider
    click = ClickPayment(
        merchant_id=config.click_merchant_id,
        service_id=config.click_service_id,
        secret_key=config.click_secret_key.get_secret_value() if config.click_secret_key else None,
        test_mode=config.click_test_mode
    )
    
    # Create invoice
    invoice = await click.create_invoice(
        amount=50000.0,
        order_id=f"Q{question_id}",
        description=f"Yuridik maslahat #{question_id}"
    )
    
    # Save payment to database
    from bot.services.payment_service import PaymentService
    payment = await PaymentService.create_online_payment(
        session=session,
        question_id=question_id,
        amount=50000.0,
        payment_method="click",
        invoice_id=invoice['invoice_id'],
        payment_url=invoice['payment_url']
    )
    
    test_notice = "\n\n⚠️ <b>TEST REJIM</b> - API kalitlar kiritilganda real to'lovlar faollashadi" if invoice.get('test_mode') else ""
    
    await callback.message.edit_text(
        f"🔵 <b>Click to'lov</b>\n\n"
        f"💰 Summa: 50,000 so'm\n"
        f"🆔 Invoice: <code>{invoice['invoice_id']}</code>\n\n"
        f"<b>To'lov qilish uchun:</b>\n"
        f"Quyidagi tugmani bosib to'lovni amalga oshiring.{test_notice}",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 To'lov sahifasiga o'tish", url=invoice['payment_url'])]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_payme:"))
async def process_payme_payment(callback: types.CallbackQuery, session: AsyncSession):
    question_id = int(callback.data.split(":")[1])
    
    from bot.payments.payme import PaymePayment
    from bot.config import config
    
    # Initialize Payme provider
    payme = PaymePayment(
        merchant_id=config.payme_merchant_id,
        secret_key=config.payme_secret_key.get_secret_value() if config.payme_secret_key else None,
        test_mode=config.payme_test_mode
    )
    
    # Create invoice
    invoice = await payme.create_invoice(
        amount=50000.0,
        order_id=f"Q{question_id}",
        description=f"Yuridik maslahat #{question_id}"
    )
    
    # Save payment to database
    from bot.services.payment_service import PaymentService
    payment = await PaymentService.create_online_payment(
        session=session,
        question_id=question_id,
        amount=50000.0,
        payment_method="payme",
        invoice_id=invoice['invoice_id'],
        payment_url=invoice['payment_url']
    )
    
    test_notice = "\n\n⚠️ <b>TEST REJIM</b> - API kalitlar kiritilganda real to'lovlar faollashadi" if invoice.get('test_mode') else ""
    
    await callback.message.edit_text(
        f"🟢 <b>Payme to'lov</b>\n\n"
        f"💰 Summa: 50,000 so'm\n"
        f"🆔 Invoice: <code>{invoice['invoice_id']}</code>\n\n"
        f"<b>To'lov qilish uchun:</b>\n"
        f"Quyidagi tugmani bosib to'lovni amalga oshiring.{test_notice}",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💳 To'lov sahifasiga o'tish", url=invoice['payment_url'])]
        ]),
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
        "✅ <b>To'lov tasdiqlovchi hujjat qabul qilindi</b>\n\n"
        "🔍 Holati: <b>🟡 Ko'rib chiqilmoqda</b>\n\n"
        "Administrator to'lovni tasdiqlagach, malakali advokat savolingizga "
        "javob tayyorlaydi.\n\n"
        "<i>📜 Holat: '📜 Mening murojaatlarim' bo'limida kuzating.</i>",
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
        "👨‍⚖️ Advokat: Azizbek To'ymurodov\n"
        "📞 Telefon: <code>+998 33 012 20 50</code>\n"
        "📍 Manzil: Toshkent shahar, Chilonzor tumani, 20-mavze.",
        parse_mode="HTML"
    )
