from aiogram import Bot, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from keyboards import main_menu, main_menu_inline, subscribe_keyboard
from texts import (
    SUBSCRIBE_TEXT,
    WELCOME_BACK_TEXT,
    WELCOME_NEW_TEXT,
    WELCOME_REFERRED_TEXT,
)
from utils import is_subscribed, pending_referrals, register_refer

start_router = Router()


@start_router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject, bot: Bot) -> None:
    """'/start' buyrug'ini qayta ishlaydi.

    Avval kanalga a'zolik tekshiriladi. A'zo bo'lmagan foydalanuvchi
    referal havola/statistikadan foydalana olmaydi va referali
    (inviter_id) keyingi tasdiqlash uchun xotirada saqlanadi.
    """
    user_id = message.from_user.id

    # Referral link bilan kelgan, lekin hali ro'yxatdan o'tmagan foydalanuvchining
    # inviter_id yodda saqlanadi — obuna tasdiqlanganidan keyin ishlatiladi.
    if command.args:
        try:
            inviter_id = int(command.args)
            if inviter_id and inviter_id != user_id:
                pending_referrals.setdefault(user_id, inviter_id)
        except (ValueError, TypeError):
            pass

    # Kanalinga haqiqiy a'zolik tekshiruvi
    if not await is_subscribed(bot, user_id):
        await message.answer(
            SUBSCRIBE_TEXT,
            reply_markup=subscribe_keyboard(),
        )
        return

    # Obuna bor — ro'yxatdan o'tkazamiz va referalni (agar bo'lsa) hisoblaymiz
    payload = pending_referrals.pop(user_id, None)
    referred, new_user = await register_refer(
        bot,
        user_id,
        message.from_user.full_name,
        message.from_user.username,
        payload,
    )

    name = message.from_user.first_name
    if not new_user:
        await message.answer(
            WELCOME_BACK_TEXT.format(name=name),
            reply_markup=main_menu_inline(),
        )
    elif referred:
        await message.answer(
            WELCOME_REFERRED_TEXT.format(name=name),
            reply_markup=main_menu_inline(),
        )
    else:
        await message.answer(
            WELCOME_NEW_TEXT.format(name=name),
            reply_markup=main_menu_inline(),
        )