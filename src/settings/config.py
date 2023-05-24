from aiogram import Dispatcher

from src.tgbot.handlers.commands import register_commands
from src.tgbot.handlers.message_wrappers import register_message
from src.tgbot.misc.default_command import set_commands


async def register_all_services(dp: Dispatcher):
    register_commands(dp)
    register_message(dp)
    await set_commands(dp)
