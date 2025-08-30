import asyncio
from telegram.bot import dp, bot
from telegram.handlers.commands import router
from telegram.handlers.messages import router_message
from telegram.handlers.admin import router_admin
from telegram.handlers.load_photos import router_photos
from telegram.handlers.auction import router_auction

from db.init_db import init_models
from db.ensure_db import ensure_database_exists



async def main():
    # await clear_table("users")
    await ensure_database_exists()
    await init_models()

    dp.include_router(router_auction)
    dp.include_router(router_photos)
    dp.include_router(router_admin)
    dp.include_router(router)
    dp.include_router(router_message)




    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())