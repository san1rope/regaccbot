from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter

from tg_bot.misc.throttling_func import rate_limit


@rate_limit(30)
async def unknown(message: types.Message):
    await message.answer(f"Unknown command - {message.text}")


def register_unknown_cmd(dp: Dispatcher):
    dp.register_message_handler(unknown, ChatTypeFilter(types.ChatType.PRIVATE))
