from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.keyboards.user import get_main_kb
from bot.keyboards.admin import get_admin_main_kb
from bot.config import config

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    
    # Register user in DB
    from bot.database import crud
    from bot.database.models import UserRole
    user = await crud.get_user_by_telegram_id(session, message.from_user.id)
    is_new_user = user is None
    if not user:
        await crud.create_user(session, message.from_user.id, UserRole.USER)

    if message.from_user.id == config.admin_id:
        await message.answer("Xush kelibsiz, Admin! Boshqaruv paneli:", reply_markup=get_admin_main_kb())
    else:
        if is_new_user:
            # New user - show registration/welcome flow
            welcome_text = (
                f"🎉 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
                "🏛️ <b>AHD Yuridik Maslahat Xizmati</b> botiga xush kelibsiz!\n"
                "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                "<b>⚖️ Xizmat ko'rsatish tartibi:</b>\n\n"
                "1️⃣ <b>Murojaat yuborish</b> - Huquqiy muammoingizni batafsil bayon qiling\n"
                "2️⃣ <b>Konsultatsiya to'lovi</b> - 50,000 so'm (to'lov chekini yuboring)\n"
                "3️⃣ <b>Tasdiqlanish</b> - Administrator to'lovni tasdiqlaydi\n"
                "4️⃣ <b>Professional maslah</b> - Malakali advokat javob beradi\n\n"
                "<i>Davom etish uchun pastdagi menyudan foydalaning 👇</i>"
            )
        else:
            # Returning user - simple welcome
            welcome_text = (
                f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
                "🏛️ <b>AHD Yuridik Maslahat</b>ga qaytganingizdan xursandmiz.\n"
                "Quyidagi menyudan kerakli xizmatni tanlang:"
            )
        
        await message.answer(welcome_text, reply_markup=get_main_kb(), parse_mode="HTML")

@router.message(F.text == "🏠 Foydalanuvchi menyusi")
async def go_to_user_menu(message: types.Message):
    await message.answer("Foydalanuvchi menyusiga o'tildi:", reply_markup=get_main_kb())

@router.message(F.text == "ℹ️ Ma'lumot")
async def cmd_info(message: types.Message):
    info_text = (
        "<b>Bot qanday ishlaydi?</b>\n\n"
        "1. 'Savol berish' tugmasini bosing.\n"
        "2. Savolingizni batafsil yozing.\n"
        "3. To'lovni amalga oshiring va chekni yuboring.\n"
        "4. Admin tasdiqlagach, javobingizni shu yerda olasiz."
    )
    await message.answer(info_text, parse_mode="HTML")

@router.message(Command("cancel"))
@router.message(F.text == "🚫 Bekor qilish")
@router.callback_query(F.data == "cancel_action")
async def cmd_cancel(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = "Amal bekor qilindi."
    if isinstance(event, types.Message):
        if event.from_user.id == config.admin_id:
            await event.answer(text, reply_markup=get_admin_main_kb())
        else:
            await event.answer(text, reply_markup=get_main_kb())
    else:
        await event.message.answer(text, reply_markup=get_main_kb())
        await event.answer()
