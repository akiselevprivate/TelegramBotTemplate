from aiogram import types
from src.settings.const import CHAT_LINK


def sub_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Подписаться", url=CHAT_LINK))
    return keyboard


# def examples_keyboard():
#     button = types.InlineKeyboardButton('Показать примеры', callback_data='examples')
#     keyboard = types.InlineKeyboardMarkup().add(button)
#     return keyboard
