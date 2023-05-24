import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.settings.const import BOT_TOKEN
from src.settings.config import register_all_services
from src.settings.logger import logger
from src.tgbot.database.sqlite_db import db


async def main():
    logger.info("Starting Bot")

    storage = MemoryStorage()

    bot = Bot(BOT_TOKEN, parse_mode="HTML")

    dp = Dispatcher(bot, storage=storage)
    await register_all_services(dp)

    # @dp.callback_query_handler(lambda c: c.data == 'examples')
    # async def process_callback_button1(callback_query: types.CallbackQuery):
    #     await bot.answer_callback_query(callback_query.id)
    #     await bot.send_message(callback_query.from_user.id, examples_text)

    db.setup()

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped")
