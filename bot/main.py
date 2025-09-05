import asyncio
from telegram.bot import dp, bot
from telegram.handlers.commands import router
from telegram.handlers.messages import router_message
from telegram.handlers.admin import router_admin
from telegram.handlers.load_photos import router_photos
from telegram.handlers.auction import router_auction

from db.init_db import init_models

from api import app  # FastAPI внутри бота
import uvicorn

async def start_bot():
    # await clear_table("users")
    await init_models()

    dp.include_router(router_auction)
    dp.include_router(router_photos)
    dp.include_router(router_admin)
    dp.include_router(router)
    dp.include_router(router_message)




    await dp.start_polling(bot, skip_updates=True)


async def start_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    # Запускаем бота и FastAPI параллельно
    await asyncio.gather(
        start_bot(),
        start_api()
    )


if __name__ == "__main__":
    asyncio.run(main())