from aiogram import Bot, F, Router
from aiogram.types import Message

from database import get_referral_count
from keyboards import main_menu, subscribe_keyboard
from texts import SUBSCRIBE_TEXT
from utils import is_subscribed

menu_router = Router()


@menu_router.message(F.text == "🔗 Referral havola")
async def referral_link_handler(message: Message, bot: Bot) -> None:
    """Foydalanuvchining shaxsiy taklif havolasini yuboradi.

    Avval kanalga a'zolik tekshiriladi — a'zo bo'lmaganlaga havola berilmaydi.
    """
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            SUBSCRIBE_TEXT,
            reply_markup=subscribe_keyboard(),
        )
        return

    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={message.from_user.id}"
    await message.answer(
        "🔗 Sizning taklif havolangiz:\n\n"
        f"{link}\n\n"
        "Havolani do'stlaringizga yuboring — ular qo'shilganda siz ball olasiz!"
    )


@menu_router.message(F.text == "📊 Statistika")
async def stats_handler(message: Message, bot: Bot) -> None:
    """Foydalanuvchining taklif qilganlar sonini ko'rsatadi."""
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            SUBSCRIBE_TEXT,
            reply_markup=subscribe_keyboard(),
        )
        return

    count = await get_referral_count(message.from_user.id)
    await message.answer(
        f"📊 Statistika:\n\n"
        f"Taklif qilganlar soni: {count}",
        reply_markup=main_menu(),
    )