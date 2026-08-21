from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message

from config import CHANNEL_LINK
from database import get_referral_count
from keyboards import main_menu, main_menu_inline, subscribe_keyboard
from texts import (
    JOIN_REQUEST_DENIED,
    JOIN_REQUEST_APPROVED,
    PRIVATE_ACCESS_NOT_READY,
    PRIVATE_ACCESS_READY,
    PRIVATE_ACCESS_TEXT,
    SUBSCRIBE_TEXT,
)
from utils import is_subscribed, _progress_bar

menu_router = Router()


async def _send_referral(message: Message, bot: Bot) -> None:
    """Referral havolasini yuborish logikasi (inline va oddiy chaqiruvi uchun umumiy)."""
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
        "Havolani do'stlaringizga yuboring — ular qo'shilganda siz ball olasiz!",
        reply_markup=main_menu_inline(),
    )


async def _send_stats(message: Message, bot: Bot) -> None:
    """Statistikani yuborish logikasi."""
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
        reply_markup=main_menu_inline(),
    )


async def _send_private(message: Message, bot: Bot) -> None:
    """Maxfiy kanal ma'lumotini yuborish logikasi."""
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            SUBSCRIBE_TEXT,
            reply_markup=subscribe_keyboard(),
        )
        return

    user_id = message.from_user.id
    count = await get_referral_count(user_id)

    from config import REQUIRED_REFERRALS, PRIVATE_CHANNEL_ID, PRIVATE_CHANNEL_LINK

    if count >= REQUIRED_REFERRALS:
        invite_link = PRIVATE_CHANNEL_LINK
        try:
            invite_link = await bot.export_chat_invite_link(PRIVATE_CHANNEL_ID)
        except Exception:
            pass

        keyboard = main_menu_inline()
        # Qo'shimcha "Kanalga o'tish" tugmasi bilan
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔓 Kanalga o'tish",
                        url=invite_link,
                    )
                ],
                *keyboard.inline_keyboard,  # boshqa menyu tugmalari
            ]
        )
        await message.answer(
            PRIVATE_ACCESS_TEXT.format(
                required=REQUIRED_REFERRALS,
                count=count,
                progress=_progress_bar(count, REQUIRED_REFERRALS),
                status=PRIVATE_ACCESS_READY,
            ),
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            PRIVATE_ACCESS_TEXT.format(
                required=REQUIRED_REFERRALS,
                count=count,
                progress=_progress_bar(count, REQUIRED_REFERRALS),
                status=PRIVATE_ACCESS_NOT_READY,
            ),
            reply_markup=main_menu_inline(),
        )


# --- Oddiy matn (ReplyKeyboard) handlerlari — eskicha moslik uchun ---

@menu_router.message(F.text == "🔗 Referral havola")
async def referral_link_handler(message: Message, bot: Bot) -> None:
    await _send_referral(message, bot)


@menu_router.message(F.text == "📊 Statistika")
async def stats_handler(message: Message, bot: Bot) -> None:
    await _send_stats(message, bot)


@menu_router.message(F.text == "🔓 Maxfiy kanal")
async def private_handler(message: Message, bot: Bot) -> None:
    await _send_private(message, bot)


# --- Inline (Callback) handlerlari — yangi inline tugmalar uchun ---

@menu_router.callback_query(F.data == "menu_referral")
async def referral_callback(callback: CallbackQuery, bot: Bot) -> None:
    await _send_referral(callback.message, bot)
    await callback.answer()


@menu_router.callback_query(F.data == "menu_stats")
async def stats_callback(callback: CallbackQuery, bot: Bot) -> None:
    await _send_stats(callback.message, bot)
    await callback.answer()


@menu_router.callback_query(F.data == "menu_private")
async def private_callback(callback: CallbackQuery, bot: Bot) -> None:
    await _send_private(callback.message, bot)
    await callback.answer()