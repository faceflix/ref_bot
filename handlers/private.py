from aiogram import Bot, F, Router
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import (
    PRIVATE_CHANNEL_ID,
    PRIVATE_CHANNEL_LINK,
    REQUIRED_REFERRALS,
)
from database import get_referral_count
from keyboards import main_menu, subscribe_keyboard
from texts import (
    JOIN_REQUEST_APPROVED,
    JOIN_REQUEST_DENIED,
    PRIVATE_ACCESS_NOT_READY,
    PRIVATE_ACCESS_READY,
    PRIVATE_ACCESS_TEXT,
    SUBSCRIBE_TEXT,
)
from utils import is_subscribed

private_router = Router()


def _progress_bar(count: int, required: int) -> str:
    """Takliflar sonini ko'rsatadigan oddiy progress bar."""
    filled = min(count, required)
    return "▰" * filled + "▱" * (required - filled)


@private_router.message(F.text == "🔓 Maxfiy kanal")
async def private_channel_handler(message: Message, bot: Bot) -> None:
    """'🔓 Maxfiy kanal' tugmasi bosilganda kirish holatini ko'rsatadi."""
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            SUBSCRIBE_TEXT,
            reply_markup=subscribe_keyboard(),
        )
        return

    user_id = message.from_user.id
    count = await get_referral_count(user_id)

    if count >= REQUIRED_REFERRALS:
        # Maxfiy kanalga o'tish havolasini olamiz (bot admin bo'lishi kerak)
        invite_link = PRIVATE_CHANNEL_LINK
        try:
            invite_link = await bot.export_chat_invite_link(PRIVATE_CHANNEL_ID)
        except Exception:
            # API xatosi bo'lsa .env dagi fallback havola ishlatiladi
            pass

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔓 Kanalga o'tish",
                        url=invite_link,
                    )
                ]
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
            reply_markup=main_menu(),
        )


@private_router.chat_join_request()
async def handle_join_request(request: ChatJoinRequest, bot: Bot) -> None:
    """Maxfiy kanalga a'zolik so'rovi kelganda referral soniga qarab qaror qiladi."""
    # Faqat maxfiy kanaldagi so'rovlarni ko'rib chiqamiz
    if str(request.chat.id) != str(PRIVATE_CHANNEL_ID):
        return

    user_id = request.from_user.id
    count = await get_referral_count(user_id)

    if count >= REQUIRED_REFERRALS:
        # Referral soni yetarli — so'rovni tasdiqlaymiz
        try:
            await bot.approve_chat_join_request(PRIVATE_CHANNEL_ID, user_id)
        except Exception:
            return

        try:
            await bot.send_message(user_id, JOIN_REQUEST_APPROVED)
        except Exception:
            # Foydalanuvchi botni bloklagan bo'lishi mumkin
            pass
    else:
        # Referral soni yetarli emas — so'rovni rad etamiz
        try:
            await bot.decline_chat_join_request(PRIVATE_CHANNEL_ID, user_id)
        except Exception:
            return

        try:
            await bot.send_message(
                user_id,
                JOIN_REQUEST_DENIED.format(
                    required=REQUIRED_REFERRALS,
                    count=count,
                ),
            )
        except Exception:
            pass