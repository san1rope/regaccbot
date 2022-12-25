import asyncio
import logging

from typing import Union
from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

logger = logging.getLogger(__name__)


class Throttling(BaseMiddleware):
    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix="antiflood_"):
        self.limit = limit
        self.prefix = key_prefix
        super(Throttling, self).__init__()

    async def throttle(self, target: Union[types.Message, types.CallbackQuery]):
        handler = current_handler.get()
        if not handler:
            return

        dp = Dispatcher.get_current()

        limit = getattr(handler, "throttling_rate_limit", self.limit)
        key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")

        try:
            await dp.throttle(key, rate=limit)
        except Throttled as t:
            await self.target_throttled(target, t, dp, key)
            raise CancelHandler()

    async def target_throttled(self, target: Union[types.Message, types.CallbackQuery], throttled: Throttled,
                               dp: Dispatcher, key: str):
        msg = target.message if isinstance(target, types.CallbackQuery) else target
        delta = throttled.rate - throttled.delta
        if isinstance(target, types.CallbackQuery):
            target = target.message

        if throttled.exceeded_count == 2:
            await target.reply("Antiflood: Stop spamming or the chat room will be blocked! \n"
                               "It hasn't been 30 seconds yet!")
            return
        elif throttled.exceeded_count == 3:
            await target.reply(f"Antiflood: Chat blocked for {round(delta)} seconds! It hasn't been 30 seconds yet!")
        await asyncio.sleep(delta)

        thr = await dp.check_key(key)
        if thr.exceeded_count == throttled.exceeded_count:
            await target.answer("Antiflood: Chat unblocked!")

    async def on_process_message(self, message: types.Message, data: dict):
        await self.throttle(message)

    async def on_process_callback_query(self, call: types.CallbackQuery, data: dict):
        await self.throttle(call)
