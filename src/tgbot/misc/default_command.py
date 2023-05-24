from aiogram import types, Dispatcher


async def set_commands(dp: Dispatcher):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Инструкция"),
        types.BotCommand("examples", "Показать примеры задач"),
        types.BotCommand("help", "Помощь"),
    ])