from aiogram import types

from src.settings.const import help_text, examples_text
from src.tgbot.handlers.users import user_start


async def help_message(message: types.Message):
    await message.bot.send_message(message.chat.id, help_text)


# async def examples_message(message: types.Message):
#     await message.bot.send_message(message.chat.id, examples_text)


def register_commands(dp):
    dp.register_message_handler(user_start, state="*", commands=["start"])
    # dp.register_message_handler(examples_message, state="*", commands=["examples"])
    dp.register_message_handler(help_message, state="*", commands=["help"])
