import os

from dotenv import load_dotenv

# .env faylidan muhit o'zgaruvchilarini yuklash
load_dotenv()

# Bot tokeni (https://t.me/BotFather orqali olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# SQLite ma'lumotlar bazasi faylining yo'li
DB_PATH = os.getenv("DB_PATH", "referral_bot.db")

# Majburiy a'zolik kanali.
# CHANNEL_ID: "@kanal_username" yoki sonli ID (-100...)
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Kanalga o'tadigan havola (Tekshirish tugmasidagi "A'zo bo'lish" tugmasida ishlatiladi)
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/")

# MAXFIY kanal (qimmatli materiallar). Bot bu kanalga ham ADMIN bo'lishi shart.
# Kanalingda "Approve join requests / A'zolik so'rovini tasdiqlash" yoqilgan bo'lsin.
# @ username bo'lmaydi — sonli ID yoziladi (masalan -1001234567890).
PRIVATE_CHANNEL_ID = os.getenv("PRIVATE_CHANNEL_ID")

# Maxfiy kanalga o'tish uchun havola (agar export_chat_invite_link ishlamasa ishlatiladi)
PRIVATE_CHANNEL_LINK = os.getenv("PRIVATE_CHANNEL_LINK", "https://t.me/")

# Maxfiy kanalga kirish uchun kerak bo'ladigan referral (taklif) soni
REQUIRED_REFERRALS = int(os.getenv("REQUIRED_REFERRALS", "5"))