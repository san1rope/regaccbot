import logging
import asyncio

from aiogram import types, Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tg_bot.config import load_config
from tg_bot.models.db_gino import db
from tg_bot.models import db_gino

# Import middlewares
from tg_bot.middlewares.throttling import Throttling
from tg_bot.middlewares.access_restriction import AccRest

# Import handlers
from tg_bot.handlers.start import register_cmd_start
from tg_bot.handlers.register import register_cmd_regacc
from tg_bot.handlers.update_password import register_cmd_upd_pass
from tg_bot.handlers.unknown import register_unknown_cmd

logger = logging.getLogger(__name__)


def register_all_middlewares(dp: Dispatcher):
    dp.setup_middleware(Throttling())
    dp.setup_middleware(AccRest())


def register_all_handlers(dp: Dispatcher):
    register_cmd_start(dp)
    register_cmd_regacc(dp)
    register_cmd_upd_pass(dp)
    register_unknown_cmd(dp)


async def connect_to_db():
    await db_gino.on_startup(dp)
    await db.gino.drop_all()  # Deletes all tables on startup.
    await db.gino.create_all()  # Creates all tables on startup.


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    config = load_config('.env')
    bot = Bot(config.tg_bot.token, parse_mode=types.ParseMode.HTML)
    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    connect_to_db()
    bot['config'] = config

    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_db())

    register_all_middlewares(dp)
    register_all_handlers(dp)

    executor.start_polling(dp, skip_updates=True)
