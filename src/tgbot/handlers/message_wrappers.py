import tempfile
import os
from pydub import AudioSegment
import inspect
from typing import TextIO, BinaryIO


from aiogram import Dispatcher, types
import src.settings.const as const
from src.settings.logger import logger
from src.tgbot.analysis.actions import (amplitude_answer, amplitude_error,
                                        amplitude_question,
                                        amplitude_wrong_content, amplitude_stage)
from src.tgbot.database.sqlite_db import db
from src.tgbot.handlers.users import check_allow, registration

from aiogram.dispatcher.filters import MediaGroupFilter

import src.tgbot.handlers.handlers as handlers


async def check_user(message: types.Message):
    await amplitude_stage(message, "check_user", "started")
    # Register user if not registered
    if not db.check_user_registered(message.from_user.id):
        await registration(message)
    # Check is user allowed to use bot
    allow, use_token = await check_allow(message)
    await amplitude_stage(message, "check_user", "completed")
    if not allow:
        return False, use_token
    return True, use_token


def split_long_string(text, max_length):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    # Append the last remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def major_wrapper(message: types.Message, action_type, action_function, action_handler, return_handler_function):
    await amplitude_stage(message, f"{action_type}_handling", "started")

    check, use_token = await check_user(message)
    if not check:
        return

    mes_to_edit = await message.bot.send_message(message.chat.id, const.streaming_answer)

    action_function_responce = await action_function(message)

    try:
        await message.bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    except:
        pass

    try:

        message_answer = await action_handler(message, action_function_responce)

    except Exception as error:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=mes_to_edit.message_id,
            text=const.generating_answer_error,
        )
        await amplitude_error(message, error)
        await amplitude_stage(message, f"{action_type}_handling", "failed")
        return

    sent_message_ids = await return_handler_function(message, mes_to_edit, message_answer)

    message_ids = [message.message_id] + sent_message_ids

    db.add_user_action(message.from_user.id,
                       message.from_user.username, action_type)
    if use_token:
        db.use_token(message.from_user.id)

    for mes_id in message_ids:
        await message.bot.forward_message(const.MEDIA_FORWARD_CHAT_ID, from_chat_id=message.chat.id, message_id=mes_id)

    await amplitude_stage(message, f"{action_type}_handling", "completed")


async def text_return_message(message: types.Message, message_to_edit: types.Message, message_answer):
    sent_message_ids = []
    message_answer_chunks = split_long_string(message_answer, 4096)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_to_edit.message_id,
        text=message_answer_chunks[0],
    )

    sent_message_ids.append(message_to_edit.message_id)

    if len(message_answer_chunks) > 1:
        for chunk in message_answer_chunks[1:]:
            mes = await message.bot.send_message(
                chat_id=message.chat.id,
                text=chunk,
            )
            sent_message_ids.append(mes.message_id)
    try:
        db.add_message_a(message.from_user.id, message.text,
                         message_answer, message_answer)
    except Exception as error:
        text_error = (
            f"Не смог записать ответ в базу от {message.from_user.id}\n"
            f" >>> {error}")
        # logger.info(text_error)
        await amplitude_error(message, text_error)

    await amplitude_answer(message, message_answer)
    return sent_message_ids


async def text_action_function(message: types.Message):
    return message.text


async def text_wrapper(message: types.Message):
    await major_wrapper(message, action_type='text', action_function=text_action_function, action_handler=handlers.handle_text, return_handler_function=text_return_message)


async def photo_action_function(message: types.Message) -> BinaryIO:
    photo = message.photo[-1]
    file_id = photo.file_id
    # Download the image
    file = await message.bot.get_file(file_id)
    # Create temporary file
    _, downloaded_file_path = tempfile.mkstemp('.jpg')
    # Specify the destination_file path to save the image
    await file.download(destination_file=downloaded_file_path)
    return open(downloaded_file_path, 'rb')


async def photo_return_message(message: types.Message, message_to_edit: types.Message, message_answer: str):
    await message_to_edit.delete()
    # url
    sent_message = await message.bot.send_photo(message.chat.id, photo=message_answer)
    return [sent_message.message_id]


async def photo_wrapper(message: types.Message):
    await major_wrapper(message, action_type='photo', action_function=photo_action_function, action_handler=handlers.handle_photo, return_handler_function=photo_return_message)


async def audio_action_function(message: types.Message) -> BinaryIO:
    if message.voice:
        file_id = message.voice.file_id
        file_extension = "ogg"
    else:
        file_id = message.audio.file_id
        file_extension = message.audio.mime_type.split('/')[-1]
    file = await message.bot.get_file(file_id)

    # Create temporary file
    _, downloaded_file_path = tempfile.mkstemp('.' + file_extension)
    # Create temporary file
    _, converted_file_path = tempfile.mkstemp('.mp3')

    # Download audio file
    await message.bot.download_file(file.file_path, downloaded_file_path)

    AudioSegment.from_file(downloaded_file_path).export(
        converted_file_path, format="mp3")

    return open(converted_file_path, 'rb')


async def audio_return_message(message: types.Message, message_to_edit: types.Message, message_answer: BinaryIO):
    await message_to_edit.delete()
    sent_message = await message.bot.send_audio(message.chat.id, audio=message_answer)
    return [sent_message.message_id]


async def voice_return_message(message: types.Message, message_to_edit: types.Message, message_answer: BinaryIO):
    await message_to_edit.delete()
    sent_message = await message.bot.send_voice(message.chat.id, voice=message_answer)
    return [sent_message.message_id]


async def audio_wrapper(message: types.Message):
    await major_wrapper(message, action_type='audio', action_function=audio_action_function, action_handler=handlers.handle_audio, return_handler_function=audio_return_message)


async def voice_wrapper(message: types.Message):
    await major_wrapper(message, action_type='voice', action_function=audio_action_function, action_handler=handlers.handle_voice, return_handler_function=voice_return_message)


async def video_action_function(message: types.Message) -> BinaryIO:
    file = await message.bot.get_file(message.video.file_id)
    file_url = f"https://api.telegram.org/file/bot{const.BOT_TOKEN}/{file.file_path}"
    _, downloaded_file_path = tempfile.mkstemp('.mp4')
    await file.download(destination_file=downloaded_file_path)
    return open(downloaded_file_path, 'rb')


async def video_return_message(message: types.Message, message_to_edit: types.Message, message_answer: BinaryIO):
    await message_to_edit.delete()
    sent_message = await message.bot.send_video(message.chat.id, video=message_answer)
    return [sent_message.message_id]


async def video_wrapper(message: types.Message):
    await major_wrapper(message, action_type='video', action_function=video_action_function, action_handler=handlers.handle_video, return_handler_function=video_return_message)


async def handle_wrong_content(message: types.Message):
    await amplitude_wrong_content(message)
    await message.bot.send_message(message.chat.id, const.wrong_content)


def register_message(dp: Dispatcher):
    dp.register_message_handler(text_wrapper,
                                state="*")
    dp.register_message_handler(handle_wrong_content,
                                MediaGroupFilter(is_media_group=True),
                                content_types=types.ContentType.PHOTO,
                                state="*")
    dp.register_message_handler(photo_wrapper,
                                content_types=types.ContentType.PHOTO,
                                state="*")
    dp.register_message_handler(handle_wrong_content,
                                content_types=types.ContentType.ANIMATION,
                                state="*")
    dp.register_message_handler(video_wrapper,
                                content_types=types.ContentType.VIDEO,
                                state="*")
    dp.register_message_handler(audio_wrapper,
                                content_types=types.ContentType.AUDIO,
                                state="*")
    dp.register_message_handler(voice_wrapper,
                                content_types=types.ContentType.VOICE,
                                state="*")
    dp.register_message_handler(handle_wrong_content,
                                content_types=types.ContentType.DOCUMENT,
                                state="*")
