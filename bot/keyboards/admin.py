from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Pending Payments"), KeyboardButton(text="Paid Questions")]
        ],
        resize_keyboard=True
    )

def get_payment_action_kb(payment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Confirm", callback_data=f"confirm_payment:{payment_id}")
    builder.button(text="Reject", callback_data=f"reject_payment:{payment_id}")
    return builder.as_markup()

def get_question_action_kb(question_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Answer", callback_data=f"answer_question:{question_id}")
    return builder.as_markup()
