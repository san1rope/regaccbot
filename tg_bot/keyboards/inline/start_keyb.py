from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_inline = InlineKeyboardMarkup(row_width=2,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text="Register", callback_data="reg"),
                                            InlineKeyboardButton(text="Our website", callback_data="site",
                                                                 url="example.com")
                                        ],
                                        [
                                            InlineKeyboardButton(text="Change password", callback_data='updpass')
                                        ]
                                    ])
