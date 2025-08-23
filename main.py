import asyncio
from telegram.bot import dp, bot
from telegram.handlers.commands import router
from telegram.handlers.messages import router_message
from telegram.handlers.admin import router_admin
from telegram.handlers.load_photos import router_photos

from db.init_db import init_models


from test import clear_table

async def main():
    # await clear_table("users")
    await init_models()
    dp.include_router(router_photos)
    dp.include_router(router_admin)
    dp.include_router(router)
    dp.include_router(router_message)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())