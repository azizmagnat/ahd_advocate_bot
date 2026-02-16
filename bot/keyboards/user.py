from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ask Question"), KeyboardButton(text="My Questions")]
        ],
        resize_keyboard=True
    )

def get_pay_command_kb(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="I have paid", callback_data=f"pay:{question_id}")
    return builder.as_markup()
