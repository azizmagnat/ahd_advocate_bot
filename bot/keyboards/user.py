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
    builder.button(text="💳 To'lov usulini tanlash", callback_data=f"select_payment_method:{question_id}")
    return builder.as_markup()

def get_payment_method_kb(question_id: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting payment method"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Onlayn to'lov (Click/Payme)", callback_data=f"online_payment:{question_id}")
    builder.button(text="📸 Chek yuborish", callback_data=f"manual_payment:{question_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_online_provider_kb(question_id: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting online payment provider"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔵 Click", callback_data=f"pay_click:{question_id}")
    builder.button(text="🟢 Payme", callback_data=f"pay_payme:{question_id}")
    builder.button(text="◀️ Orqaga", callback_data=f"select_payment_method:{question_id}")
    builder.adjust(2, 1)
    return builder.as_markup()
