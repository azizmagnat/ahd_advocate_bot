from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Kutilayotgan to'lovlar"), KeyboardButton(text="📩 To'langan savollar")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🏠 Foydalanuvchi menyusi")]
        ],
        resize_keyboard=True
    )

def get_payment_action_kb(payment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"confirm_payment:{payment_id}")
    builder.button(text="❌ Rad etish", callback_data=f"reject_payment:{payment_id}")
    return builder.as_markup()

def get_question_action_kb(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Javob yozish", callback_data=f"answer_question:{question_id}")
    return builder.as_markup()
