from src.tgbot.analysis.amplitude import amp
from src.tgbot.database.sqlite_db import db
from src.settings.logger import logger


async def send_and_log(event_name, id, event_properties=None, user_properties=None):
    try:
        res = await amp.log(id, event_name,
                            event_properties=event_properties,
                            user_properties=user_properties)
        # print('sent', res)
        logger.info(f"id: {id},\n"
                    f"event_name: {event_name},\n"
                    f"event_properties: {event_properties},\n"
                    f"user_properties: {user_properties}\n")
    except Exception as error:
        logger.error(f"Error: {error}")


async def amplitude_registration(message):
    event_name = "registration"
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       user_properties=user_properties)


async def amplitude_error(message, text_error, event_name="error", question_type="text"):
    if event_name != "error":
        event_name = "error_" + event_name
    event_properties = {"error": text_error,
                        "question": message.text, "question_type": question_type}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       event_properties=event_properties,
                       user_properties=user_properties)


async def amplitude_stage(message, stage, status):
    """ status: started, completed, failed """
    event_name = "stage_" + stage + "_" + status
    # event_properties = {"time": time}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       # event_properties=event_properties,
                       user_properties=user_properties)


async def amplitude_wrong_content(message):
    event_name = "wrong_conten_type"
    event_properties = {"content_type": message.content_type}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       event_properties=event_properties,
                       user_properties=user_properties)


async def amplitude_sub(message):
    event_name = "subscribe"
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       user_properties=user_properties)


async def amplitude_question(message, text):
    event_name = "send_question"
    event_properties = {"question": text}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       event_properties=event_properties,
                       user_properties=user_properties)


async def amplitude_answer(message, answer):
    event_name = "get_answer"
    event_properties = {"answer": answer}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       event_properties=event_properties,
                       user_properties=user_properties)


async def amplitude_ads_link(message, ad_name):
    event_name = f"ads_{ad_name}"
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       user_properties=user_properties)


async def amplitude_referral(message, referral_user_id):
    event_name = "referral"
    event_properties = {"referral_user_id": referral_user_id}
    user_properties = {"username": message.from_user.username,
                       "first_name": message.from_user.first_name,
                       "last_name": message.from_user.last_name}
    await send_and_log(event_name, message.from_user.id,
                       event_properties=event_properties,
                       user_properties=user_properties)
