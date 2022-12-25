from asyncpg import UniqueViolationError

from tg_bot.models.db_gino import db
from tg_bot.models.schemas.user import User


async def add_user(username: str, password: str):
    try:
        user = User(username=username, password=password)
        await user.create()
    except UniqueViolationError:
        pass


async def select_user(username: str = None):
    user = await User.query.where(User.username == username).gino.first()
    return user


async def update_password(username: str, password: str):
    user = await select_user(username)
    await user.update(password=password).apply()
