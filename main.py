import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers.start import router as start_router
from handlers.upload import router as upload_router
from handlers.ask import router as ask_router
from handlers.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(start_router, upload_router, ask_router, chat_router)
    
    try:
        logger.info("Starting bot polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot session closed")

if __name__ == "__main__":
    asyncio.run(main())