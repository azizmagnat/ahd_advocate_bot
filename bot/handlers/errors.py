import logging
from aiogram import Router, types
from aiogram.handlers import ErrorHandler

router = Router()

@router.errors()
async def global_exception_handler(event: types.ErrorEvent):
    from bot.config import config
    
    logging.error(f"Kutilmagan xatolik: {event.exception}", exc_info=True)
    
    # Get bot instance from update
    bot = event.update.bot if event.update else None
    exception_text = str(event.exception)
    
    if bot:
        # Notify user/admin directly in the chat with the actual error for debugging
        error_msg = (
            f"❌ <b>Xatolik yuz berdi!</b>\n\n"
            f"<b>Sababi:</b> <code>{exception_text}</code>\n\n"
            f"<i>Iltimos, ushbu xabarni ko'chirib menga yuboring.</i>"
        )
        try:
            if event.update.message:
                await event.update.message.answer(error_msg, parse_mode="HTML")
            elif event.update.callback_query:
                await event.update.callback_query.message.answer(error_msg, parse_mode="HTML")
                await event.update.callback_query.answer()
        except Exception:
            pass
