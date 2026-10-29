import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes
import aiohttp

# إعداد السجلات لمتابعة حالة البوت
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# بيانات الحساب المستهدف لشحن الأكواد
PLAYER_ID = "862212912"
ZONE_ID = "6412"
BOT_TOKEN = "9238839324:AAHQqj0ZUtQBtbNUgkp33BhjtFxxAutnF90"
CHANNEL_USERNAME = "mobilelegendsar1"

# --- سيرفر ويب وهمي لرضا منصة Render وتجنب خطأ Timed Out ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running and active!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# تشغيل السيرفر الوهمي في خلفية النظام
Thread(target=run_web_server, daemon=True).start()
# -------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! بوت شحن أكواد موبايل ليجند يعمل الآن ومستعد لمراقبة القناة.")

async def main():
    # بناء تطبيق البوت
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(telegram.ext.CommandHandler("start", start))

    # تشغيل البوت
    print("Application started")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # إبقاء البوت يعمل باستمرار
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == '__main__':
    asyncio.run(main())
