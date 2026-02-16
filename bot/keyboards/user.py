from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❓ Savol berish"), KeyboardButton(text="📜 Mening savollarim")],
            [KeyboardButton(text="ℹ️ Ma'lumot"), KeyboardButton(text="📞 Bog'lanish")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan birini tanlang"
    )

def get_pay_command_kb(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ To'lov qildim", callback_data=f"pay:{question_id}")
    builder.button(text="❌ Bekor qilish", callback_data="cancel_action")
    return builder.as_markup()
