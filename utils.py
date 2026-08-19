from aiogram import Bot

from config import CHANNEL_ID
from database import add_user, get_user, increment_referral_count
from texts import REFERRAL_BONUS_MESSAGE

# A'zo sanaladigan statuslar
SUBSCRIBED_STATUSES = {"member", "administrator", "creator"}

# Kanalga a'zo bo'lmagan holda referral link bilan kelgan foydalanuvchilarning
# inviter_id lari xotirada saqlanadi (obuna tasdiqlangach hisoblanadi).
pending_referrals: dict[int, int] = {}


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi majburiy kanalga a'zo ekanligini tekshiradi.

    Kanal sozlanmagan bo'lsa (CHANNEL_ID bo'sh) True qaytaradi (cheklov yo'q).
    """
    if not CHANNEL_ID:
        return True

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in SUBSCRIBED_STATUSES
    except Exception:
        # Foydalanuvchi topilmadi yoki bot kanalga admin qo'shilmagan
        return False


async def register_refer(
    bot: Bot,
    user_id: int,
    full_name: str,
    username: str | None,
    payload: int | None,
) -> tuple[bool, bool]:
    """Foydalanuvchini ro'yxatdan o'tkazadi va referral logikasini bajaradi.

    Referral faqat quyidagilar bajarilsagina hisoblanadi:
      - foydalanuvchi YANGI bo'lsa,
      - referal kodi yaroqli bo'lsa,
      - o'z havolasi orqali kirmagan bo'lsa,
      - taklif qiluvchi bazada mavjud bo'lsa.

    Qaytaradi: (referred: havola bo'yicha ball berildimi, new_user: yangi foydalanuvchimi)
    """
    existing = await get_user(user_id)
    if existing:
        return False, False

    referred_by = None
    if payload:
        if payload != user_id:  # foydalanuvchi o'z havolasi orqali kirmasligi kerak
            inviter = await get_user(payload)
            if inviter:
                referred_by = payload

                # Taklif qiluvchining referral_count ni +1 ga oshiramiz
                await increment_referral_count(payload)

                # Taklif qiluvchiga Telegram orqali notification yuboramiz
                try:
                    await bot.send_message(payload, REFERRAL_BONUS_MESSAGE)
                except Exception:
                    # Taklif qiluvchi botni bloklagan bo'lishi mumkin
                    pass

    # Yangi foydalanuvchini bazaga saqlaymiz (referred_by bilan yoki ularsiz)
    await add_user(user_id, full_name, username, referred_by=referred_by)
    return referred_by is not None, True