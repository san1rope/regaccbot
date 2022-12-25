from aiogram.dispatcher.filters.state import StatesGroup, State


class RegAcc(StatesGroup):
    Login = State()
    Password = State()
