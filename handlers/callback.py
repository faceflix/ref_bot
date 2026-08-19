from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from keyboards import main_menu, subscribe_keyboard
from texts import (
    WELCOME_BACK_TEXT,
    WELCOME_NEW_TEXT,
    WELCOME_REFERRED_TEXT,
)
from utils import is_subscribed, pending_referrals, register_refer

callback_router = Router()


@callback_router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot) -> None:
    """'✅ Tekshirish' tugmasi bosilganda kanalga a'zolikni qayta tekshiradi.

    Agar foydalanuvchi kanalga a'zo bo'lgan bo'lsa — uni ro'yxatdan o'tkazadi
    (saqlangan referal kod, agar bo'lsa, shunda hisoblanadi).
    """
    user_id = callback.from_user.id

    if not await is_subscribed(bot, user_id):
        await callback.answer(
            "Siz hali kanalga a'zo emassiz ❌", show_alert=True
        )
        return

    # Obuna tasdiqlandi — ro'yxatdan o'tkazamiz va referal (agar bo'lsa) hisoblanadi
    payload = pending_referrals.pop(user_id, None)
    referred, new_user = await register_refer(
        bot,
        user_id,
        callback.from_user.full_name,
        callback.from_user.username,
        payload,
    )

    # Eski (obuna so'ralgan) xabarni o'chiramiz
    try:
        await callback.message.delete()
    except Exception:
        pass

    name = callback.from_user.first_name
    if not new_user:
        await callback.message.answer(
            WELCOME_BACK_TEXT.format(name=name),
            reply_markup=main_menu(),
        )
    elif referred:
        await callback.message.answer(
            WELCOME_REFERRED_TEXT.format(name=name),
            reply_markup=main_menu(),
        )
    else:
        await callback.message.answer(
            WELCOME_NEW_TEXT.format(name=name),
            reply_markup=main_menu(),
        )

    await callback.answer()