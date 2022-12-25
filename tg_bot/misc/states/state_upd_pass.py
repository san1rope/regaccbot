from aiogram.dispatcher.filters.state import StatesGroup, State


class UpdPass(StatesGroup):
    Login = State()
    Password = State()
    New_Password = State()
