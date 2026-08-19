import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import callback_router, menu_router, private_router, start_router
from texts import BOT_DESCRIPTION, BOT_SHORT_DESCRIPTION

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    """Botni ishga tushiradi."""
    # Ma'lumotlar bazasini yaratish
    await init_db()

    # Bot va Dispatcher obyektlarini yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Handler (router) larni ulash
    dp.include_router(start_router)
    dp.include_router(callback_router)
    dp.include_router(menu_router)
    dp.include_router(private_router)

    # Bot profili matnlarini o'rnatish:
    # bu matn foydalanuvchi Start/Ochish tugmasini bosishdan oldin ko'radi
    await bot.set_my_description(BOT_DESCRIPTION)
    await bot.set_my_short_description(BOT_SHORT_DESCRIPTION)

    # Eski webhook'ni tozalab, polling'ni boshlaymiz
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())