from aiogram import types
from typing import BinaryIO


async def handle_photo(message: types.Message, photo_file: BinaryIO) -> str:

    # test url
    photo_url = "https://img.freepik.com/free-vector/gradient-car-dealer-logo-template_23-2149334632.jpg?w=1380&t=st=1684854322~exp=1684854922~hmac=e1aae7febe8759150ed392b5ab2f8b5b1dcc742f3fc813e2de1b1176b887eb08"
    return photo_url


# mp3 audio file, deleted after execution
async def handle_audio(message: types.Message, audio_file: BinaryIO) -> BinaryIO:
    return audio_file


async def handle_video(message: types.Message, video_file: BinaryIO) -> BinaryIO:
    return video_file


async def handle_text(message: types.Message, text: str) -> str:
    answer = f'Recieved this message: "{text}"'
    return answer


async def handle_voice(message: types.Message, audio_file: BinaryIO) -> BinaryIO:
    return audio_file
