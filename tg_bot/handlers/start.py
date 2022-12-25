import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import CommandStart, ChatTypeFilter, Command

from tg_bot.keyboards.inline.start_keyb import start_inline
from tg_bot.misc.throttling_func import rate_limit

logger = logging.getLogger(__name__)


@rate_limit(30)
async def start(message: types.Message):
    logger.info(f"Handler called: start. user_id={message.from_user.id}")
    text = [
        f"<b>Hello, {message.from_user.full_name}!</b>",
        "I am a bot for registering accounts",
        "Here you can create a new account at <i>example.com</i>",
        "To get started, click on <b>Register</b>",
        "Or enter the command /register",
        "You can register an account once every 30 seconds!"
    ]
    await message.answer('\n'.join(text), reply_markup=start_inline)


@rate_limit(30)
async def site(message: types.Message):
    logger.info(f"Handler called: site. user_id={message.from_user.id}")
    temp = "example.com"
    await message.answer(f"Our site: {temp}")


def register_cmd_start(dp: Dispatcher):
    dp.register_message_handler(start, ChatTypeFilter(types.ChatType.PRIVATE), CommandStart())
