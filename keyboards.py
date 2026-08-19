from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import CHANNEL_LINK


def main_menu() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalarini (ReplyKeyboardMarkup) qaytaradi."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔗 Referral havola")],
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🔓 Maxfiy kanal")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def subscribe_keyboard() -> InlineKeyboardMarkup:
    """Kanalinga a'zo bo'lish uchun inline tugmalarni qaytaradi."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga a'zo bo'lish",
                    url=CHANNEL_LINK,
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Tekshirish",
                    callback_data="check_subscription",
                )
            ],
        ]
    )
    return keyboard