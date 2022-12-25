import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, ChatTypeFilter

from tg_bot.keyboards.inline.start_keyb import start_inline
from tg_bot.misc.states.state_register import RegAcc
from tg_bot.misc.throttling_func import rate_limit
from tg_bot.models import quick_commands as db_cmd

logger = logging.getLogger(__name__)


@rate_limit(30)
async def start_register(target: types.Message | types.CallbackQuery):
    logger.info(f"Handler called: start_register. user_id={target.from_user.id}")
    text = [
        "<b>You started the registration!</b>",
        "Enter your username:",
        "<i>(3 to 15 characters)</i>",
        "Type /cancel to cancel the registration."
    ]

    if isinstance(target, types.CallbackQuery):
        await target.answer()
        await target.message.answer('\n'.join(text))
    elif isinstance(target, types.Message):
        await target.answer('\n'.join(text))

    await RegAcc.Login.set()


async def answer_login(message: types.Message, state: FSMContext):
    temp = message.text
    if temp == '/cancel':
        await message.answer("You cancelled the registration!", reply_markup=start_inline)
        await state.reset_state()
        return

    if not (3 <= len(temp) <= 15) or temp.isdigit():
        await message.reply("Wrong input format! Try again.")
        return
    elif await db_cmd.select_user(username=temp):
        await message.reply("A user with this login is already registered!"
                            "\nEnter another username!")
        return

    await state.update_data(login=temp)

    text = [
        "<b>Login accepted!</b>",
        "Make up a difficult password:",
        "<i>(5 to 30 characters)</i>",
    ]
    await message.reply('\n'.join(text))

    await RegAcc.next()


async def end_register(message: types.Message, state: FSMContext):
    temp = message.text
    if temp == '/cancel':
        await message.answer("You cancelled the registration!", reply_markup=start_inline)
        await state.reset_state()
        return

    if not (5 <= len(temp) <= 30):
        await message.reply("Wrong input format! Try again.")
        return

    await state.update_data(password=temp)
    data = await state.get_data()
    login = data['login']
    password = data['password']

    await db_cmd.add_user(username=login, password=password)

    text = [
        "<b>Password accepted!</b>",
        "<b>You have completed your registration!</b>",
        f"Your login: {login}",
        f"Your password: {password}"
    ]
    await message.reply('\n'.join(text), reply_markup=start_inline)
    logger.info(f"Completing the registration. user_id={message.from_user.id}")

    await state.finish()


def register_cmd_regacc(dp: Dispatcher):
    dp.register_message_handler(start_register, ChatTypeFilter(types.ChatType.PRIVATE), Command('register'))
    dp.register_callback_query_handler(start_register, ChatTypeFilter(types.ChatType.PRIVATE), text='reg')
    dp.register_message_handler(answer_login, state=RegAcc.Login)
    dp.register_message_handler(end_register, state=RegAcc.Password)
