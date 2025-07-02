import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers.start import router as start_router
from handlers.upload import router as upload_router
from handlers.ask import router as ask_router
from handlers.chat import router as chat_router
from aiogram.types import BotCommand

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log"
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу"),
        BotCommand(command="/help", description="Показать справку"),
        BotCommand(command="/upload", description="Загрузить файлы с Google Drive"),
        BotCommand(command="/ask", description="Задать вопрос по документам"),
        BotCommand(command="/chat", description="Начать общий диалог"),
        BotCommand(command="/reset", description="Сбросить контекст")
    ]
    await bot.set_my_commands(commands)
    logger.info("Выпадающее меню с командами успешно настроено")

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(start_router, upload_router, ask_router, chat_router)
    
    try:
        logger.info("Starting bot polling...")
        dp.startup.register(on_startup)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot session closed")

if __name__ == "__main__":
    asyncio.run(main())