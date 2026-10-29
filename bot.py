import os
import re
import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# إعداد السجلات لمتابعة السرعة والأخطاء
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = "9238839324:AAHQqj0ZUtQBtbNUgkp33BhjtFxxAutnF90"

# قائمة القنوات والمصادر التي تريد مراقبتها (أضف ما شئت هنا)
SOURCE_CHANNELS = ["mobilelegendsar1", "OtherCodeChannel2"]

# بيانات اللعبة الخاصة بك ولأصدقائك (Game ID و Zone ID)
# يمكنك إضافة عدة حسابات هنا ليقوم البوت بشحنها للجميع فوراً
ACCOUNTS = [
    {"game_id": "862212912", "zone_id": "6412"},  # حسابك
    # {"game_id": "87654321", "zone_id": "5678"}, # حساب صديقك (أزل الرمز # إذا أردت تفعيله)
]

async def redeem_code_on_site(code: str, game_id: str, zone_id: str):
    """دالة إرسال الكود وإدخاله في موقع اللعبة بأقصى سرعة"""
    url = "https://m.mobilelegends.com/en/codex" # رابط موقع الاستبدال الرسمي أو API الموقع
    payload = {
        "game_id": game_id,
        "zone_id": zone_id,
        "code": code,
        # ملاحظة: بعض المواقع تتطلب بيانات تحقق إضافية مثل Verification Code يتم جلبها برمجياً
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # إرسال طلب سريع للموقع لتفعيل الكود
            async with session.post(url, json=payload, timeout=5) as response:
                result = await response.text()
                logging.info(f"Redeem attempt for Code {code} on ID {game_id}: Success")
                return True
    except Exception as e:
        logging.error(f"Failed to redeem code {code} for ID {game_id}: {e}")
        return False

async def monitor_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if message and message.chat.username in SOURCE_CHANNELS:
        text = message.text or message.caption
        if text:
            # البحث عن الكود داخل النص (عادة يكون مكون من أحرف وأرقام إنجليزية كبيرة وبطول معين)
            # مثال: استخراج الأكواد التي تبدو ككود شحن
            found_codes = re.findall(r'\b[A-Z0-9]{10,16}\b', text)
            
            if found_codes:
                for code in found_codes:
                    logging.info(f"⚡ Fastest code detected: {code}")
                    
                    # الدوران على الحسابات المسجلة وإرسال الكود لها فوراً وبسرعة
                    for acc in ACCOUNTS:
                        asyncio.create_task(
                            redeem_code_on_site(code, acc["game_id"], acc["zone_id"])
                        )
                    
                    # إرسال تنبيه لقناتك الخاصة أو حسابك بأن البوت حاول شحن الكود
                    await context.bot.send_message(
                        chat_id="@YourChannelUsername", # استبدل بمعرف قناتك لتستلم التنبيهات
                        text=f"🔥 تم رصد كود وإرساله للموقع فوراً:\n`{code}`"
                    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ربط البوت بمراقبة عدة قنوات في نفس الوقت
    for channel in SOURCE_CHANNELS:
        app.add_handler(MessageHandler(filters.Chat(username=channel), monitor_channels))
    
    logging.info("🚀 Bot is running and monitoring all sources for instant redemption...")
    app.run_polling()

if __name__ == "__main__":
    main()
