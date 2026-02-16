from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.user import get_main_kb, get_main_kb as get_user_kb # Just reusing for now
from bot.keyboards.admin import get_admin_main_kb
from bot.config import config

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    print(f"User ID: {message.from_user.id}") # Print ID for easy copy-paste
    if message.from_user.id == config.admin_id:
        await message.answer("Welcome Admin!", reply_markup=get_admin_main_kb())
    else:
        await message.answer("Welcome! Ask a question or view your history.", reply_markup=get_main_kb())

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == config.admin_id:
         await message.answer("Actions cancelled.", reply_markup=get_admin_main_kb())
    else:
        await message.answer("Action cancelled.", reply_markup=get_main_kb())
