import aiosqlite

from config import DB_PATH


async def init_db() -> None:
    """Ma'lumotlar bazasi va 'users' jadvalini yaratadi (agar mavjud bo'lmasa)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY,
                full_name      TEXT,
                username       TEXT,
                referred_by    INTEGER,
                referral_count INTEGER NOT NULL DEFAULT 0,
                created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def get_user(user_id: int) -> dict | None:
    """Berilgan user_id bo'yicha foydalanuvchini qaytaradi (topilmasa None)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_user(
    user_id: int,
    full_name: str,
    username: str | None,
    referred_by: int | None = None,
) -> None:
    """Yangi foydalanuvchini bazaga qo'shadi.

    Agar foydalanuvchi allaqachon mavjud bo'lsa, INSERT OR IGNORE tufayli
    hech qanday o'zgarish qilinmaydi.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id, full_name, username, referred_by)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, full_name, username, referred_by),
        )
        await db.commit()


async def increment_referral_count(user_id: int) -> None:
    """Berilgan foydalanuvchining referral_count qiymatini 1 ga oshiradi."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()


async def get_referral_count(user_id: int) -> int:
    """Foydalanuvchining taklif qilganlar (referral_count) sonini qaytaradi."""
    user = await get_user(user_id)
    return user["referral_count"] if user else 0
