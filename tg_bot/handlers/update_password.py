import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, Command

from tg_bot.keyboards.inline.start_keyb import start_inline
from tg_bot.misc.states.state_upd_pass import UpdPass
from tg_bot.misc.throttling_func import rate_limit
from tg_bot.models import quick_commands as cmd_db

logger = logging.getLogger(__name__)


@rate_limit(30, 'update')
async def start_update(target: types.Message | types.CallbackQuery):
    logger.info(f"Handler called: start_update. user_id={target.from_user.id}")
    text = [
        "To change your account password",
        "Enter the login of an existing user:",
        "Type /cancel to cancel the process."
    ]

    if isinstance(target, types.CallbackQuery):
        await target.answer()
        await target.message.answer('\n'.join(text))
    elif isinstance(target, types.Message):
        await target.answer('\n'.join(text))

    await UpdPass.Login.set()


async def answer_login(message: types.Message, state: FSMContext):
    login = message.text
    if login == '/cancel':
        await message.answer("<b>You canceled the password change process!</b>", reply_markup=start_inline)
        await state.reset_state()
        return

    user = await cmd_db.select_user(username=login)
    if (user is None) or (user.username != login):
        data = await state.get_data()
        try:
            wl = data['wrong_login']
            if wl == 3:
                await message.answer("<b>Process cancelled!</b> \nYou made a mistake more than 3 times.")
                await state.reset_state()
                return
            elif wl == 2:
                await state.update_data(wrong_login=3)
            else:
                await state.update_data(wrong_login=2)
        except KeyError:
            await state.update_data(wrong_login=1)

        try:
            await message.reply(f"<b>Wrong login, try again! Attempts left: {3 - data['wrong_login']}</b>")
            return
        except KeyError:
            await message.reply(f"<b>Wrong login, try again! Attempts left: 3</b>")
            return

    await state.update_data(p_login=login)

    text = [
        "<b>The login is correct!</b>",
        "Now enter your old account password:"
    ]
    await message.reply('\n'.join(text))

    await UpdPass.next()


async def answer_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = message.text
    if password == '/cancel':
        await message.answer("<b>You canceled the password change process!</b>")
        await state.reset_state()
        return

    login = data['p_login']
    user_password = await cmd_db.select_user(username=login)
    if user_password.password != password:
        data = await state.get_data()
        try:
            wp = data['wrong_password']
            if wp == 3:
                await message.answer("<b>Process cancelled!</b> \nYou made a mistake more than 3 times.")
                await state.reset_state()
                return
            elif wp == 2:
                await state.update_data(wrong_password=3)
            else:
                await state.update_data(wrong_password=2)
        except KeyError:
            await state.update_data(wrong_password=1)

        try:
            await message.reply(f"<b>Wrong password, try again! Attempts left: {3 - data['wrong_password']}</b>")
            return
        except KeyError:
            await message.reply(f"<b>Wrong password, try again! Attempts left: 3</b>")
            return

    await state.update_data(p_password=password)

    text = [
        "<b>The password is correct!</b>",
        "Enter a new password for the account:",
        "<i>(5 to 30 characters)</i>"
    ]
    await message.reply('\n'.join(text))

    await UpdPass.next()


async def answer_new_password(message: types.Message, state: FSMContext):
    new_password = message.text
    if new_password == '/cancel':
        await message.answer("<b>You canceled the password change process!</b>")
        await state.reset_state()
        return

    if not (5 <= len(new_password) <= 30):
        await message.reply("Wrong input format! Try again.")
        return

    data = await state.get_data()
    login = data['p_login']
    await cmd_db.update_password(username=login, password=new_password)

    text = [
        "<b>Password has been successfully changed!</b>",
        f"New your password: {new_password}"
    ]
    await message.reply('\n'.join(text), reply_markup=start_inline)
    logger.info(f"Completing a password change. user_id={message.from_user.id}")

    await state.finish()


def register_cmd_upd_pass(dp: Dispatcher):
    dp.register_message_handler(start_update, ChatTypeFilter(types.ChatType.PRIVATE), Command('upd_pass'))
    dp.register_callback_query_handler(start_update, ChatTypeFilter(types.ChatType.PRIVATE), text='updpass')
    dp.register_message_handler(answer_login, state=UpdPass.Login)
    dp.register_message_handler(answer_password, state=UpdPass.Password)
    dp.register_message_handler(answer_new_password, state=UpdPass.New_Password)
