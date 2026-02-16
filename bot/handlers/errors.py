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
    
    if bot:
        # Notify Admin about the specific error
        error_msg = f"❌ <b>ADMIN DEBUG:</b>\n\n<code>{str(event.exception)[:1000]}</code>"
        try:
            await bot.send_message(config.admin_id, error_msg, parse_mode="HTML")
        except Exception:
            pass

    # Notify user politely
    if event.update.message:
        await event.update.message.answer(
            "⚠️ <b>Kutilmagan xatolik yuz berdi.</b>\n\n"
            "Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning.",
            parse_mode="HTML"
        )
    elif event.update.callback_query:
        try:
            await event.update.callback_query.message.answer(
                "⚠️ <b>Xatolik yuz berdi.</b>"
            )
            await event.update.callback_query.answer()
        except Exception:
            pass
