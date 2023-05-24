from aiogram import types
from aiogram.utils.deep_linking import get_start_link, decode_payload

from src.settings.const import CHAT_ID, CHAT_LINK, REFERRAL_SYSTEM, REFERRAL_DAILY_LIMIT, REFERRAL_INVITE_TOKENS, TEST_TRIES_LIMIT, hello_text, blocked_message, all_demo_requests_used, referral_success_text, referral_text
from src.settings.logger import logger
from src.tgbot.analysis.actions import (amplitude_error,
                                        amplitude_registration, amplitude_sub, amplitude_ads_link, amplitude_referral)
from src.tgbot.database.sqlite_db import db
from src.tgbot.keyboards.inline import sub_keyboard

keyboard_sub = sub_keyboard()


async def registration(message: types.Message):
    try:
        new_user = db.add_user(message.from_user.id,
                               message.from_user.username,
                               message.from_user.first_name,
                               message.from_user.last_name)
        if new_user:
            await amplitude_registration(message)
        return new_user
    except Exception as error:
        text_error = f'Ошибка при регистрации {message.from_user.id}:\n' \
                     f' >>> {error}'
        await amplitude_error(message, text_error)
        return False


async def check_sub(message: types.Message):
    if CHAT_ID and CHAT_LINK:
        try:
            check_user_sub = await message.bot.get_chat_member(
                chat_id=CHAT_ID, user_id=message.from_user.id)
            if check_user_sub["status"] == types.ChatMemberStatus.LEFT:
                await message.bot.delete_message(message.chat.id,
                                                 message.message_id)
                return False
        except Exception as error:
            text_error = f'Не смогли проверить пользователя ' \
                         f'{message.from_user.id}' \
                         f' на членство канала {CHAT_ID} >>> {error}'
            await amplitude_error(message, text_error)
    else:
        text_error = 'В настройках не указаны контакты канала для подписки'
        await amplitude_error(message, text_error)
    return True


async def check_allow(message: types.Message):
    try:
        block = db.get_user_block(message.from_user.id)
    except TypeError:
        await user_start(message)
        return
    if block:
        await message.bot.send_message(
            message.chat.id, blocked_message)
        return False, False
    user_actions, referral_tokens = db.get_user_action_count(
        message.from_user.id)
    if user_actions > TEST_TRIES_LIMIT:
        sub = await check_sub(message)
        if not sub:
            await message.bot.send_message(
                message.chat.id,
                text=all_demo_requests_used,
                reply_markup=keyboard_sub)
            return False, False
        else:
            if user_actions == TEST_TRIES_LIMIT + 2:
                await amplitude_sub(message)
    if REFERRAL_SYSTEM:
        last_action_count = db.get_last_user_action_count(message.from_user.id)
        if last_action_count > REFERRAL_DAILY_LIMIT:
            if referral_tokens <= 0:
                referral_link = await get_start_link(f'ref_{message.from_user.id}', encode=False)
                await message.bot.send_message(
                    message.chat.id,
                    text=referral_text)
                await message.bot.send_message(
                    message.chat.id,
                    text=referral_link)
                return False, False
            else:
                return True, True
    return True, False


async def user_start(message: types.Message):
    payload = message.get_args()
    # payload = decode_payload(args)
    if payload != '':
        if payload.startswith('ads_'):
            ad_name = payload[4:]
            await amplitude_ads_link(message, ad_name)
        elif REFERRAL_SYSTEM and payload.startswith('ref_'):
            referral_user_id = payload[4:]
            if referral_user_id == message.from_user.id:
                referral_success, referral_error = False, 'user used their own link'
            else:
                referral_success, referral_error = db.add_referral(
                    message.from_user.id, message.from_user.username, referral_user_id,  REFERRAL_INVITE_TOKENS)
            if referral_success:
                await message.bot.send_message(
                    referral_user_id,
                    text=referral_success_text)
                await amplitude_referral(message, referral_user_id)
            else:
                text_error = f'Реферальная ссылка не сработала для полдзователя ' \
                             f'{message.from_user.id}' \
                             f' от пользователя {referral_user_id} >>> {referral_error}'
                await amplitude_error(message, text_error)
    await registration(message)
    await message.bot.send_message(message.chat.id,
                                   text=hello_text)
