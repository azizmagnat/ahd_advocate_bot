import logging
from aiogram import Router, types
from aiogram.handlers import ErrorHandler

router = Router()

@router.errors()
async def global_exception_handler(event: types.ErrorEvent):
    from bot.config import config
    
    # Get bot instance from update
    bot = event.update.bot if event.update else None
    exception_name = type(event.exception).__name__
    exception_text = str(event.exception)
    
    logging.error(f"Xatolik [{exception_name}]: {exception_text}", exc_info=True)
    
    if bot:
        # Detailed error for user to report
        error_msg = (
            f"❌ <b>BOTDA XATOLIK YUZ BERDI!</b>\n\n"
            f"<b>Xato turi:</b> <code>{exception_name}</code>\n"
            f"<b>Xabari:</b> <code>{exception_text}</code>\n\n"
            f"<i>Iltimos, ushbu xabarni ko'chirib (copy) menga yuboring!</i>"
        )
        try:
            if event.update.message:
                await event.update.message.answer(error_msg, parse_mode="HTML")
            elif event.update.callback_query:
                await event.update.callback_query.message.answer(error_msg, parse_mode="HTML")
                await event.update.callback_query.answer()
        except Exception:
            pass
