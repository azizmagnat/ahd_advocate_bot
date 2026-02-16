import logging
from aiogram import Router, types
from aiogram.handlers import ErrorHandler

router = Router()

@router.errors()
async def global_exception_handler(event: types.ErrorEvent):
    logging.error(f"Kutilmagan xatolik: {event.exception}", exc_info=True)
    
    # Notify user politely
    if event.update.message:
        await event.update.message.answer(
            "⚠️ <b>Kutilmagan xatolik yuz berdi.</b>\n\n"
            "Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning.",
            parse_mode="HTML"
        )
    elif event.update.callback_query:
        await event.update.callback_query.message.answer(
            "⚠️ <b>Xatolik yuz berdi.</b>"
        )
        await event.update.callback_query.answer()
