import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
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

# قائمة أفضل وأسرع القنوات لمراقبتها في نفس الوقت
TARGET_CHANNELS = [
    "mobilelegendsar1",
    "mobileleg",
    "MLBB_Official",
    "MobileLegendsCodess"
]

# --- سيرفر ويب وهمي لرضا منصة Render وتجنب أخطاء المهلة ---
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
    await update.message.reply_text("أهلاً بك! بوت مراقبة أسرع قنوات موبايل ليجند يعمل الآن وجاهز للسهر طوال الليل.")

# دالة لمراقبة الرسائل القادمة من جميع القنوات المحددة
async def watch_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if message and message.chat.username:
        # التحقق مما إذا كانت القناة ضمن القائمة المستهدفة
        if message.chat.username in TARGET_CHANNELS:
            code_text = message.text
            logging.info(f"تم التقاط كود من القناة @{message.chat.username}: {code_text}")
            
            # إرسال تنبيه فوري لك في المحادثة الخاصة بالبوت
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=f"🚨 **كود جديد تم رصده في @{message.chat.username}**:\n\n{code_text}"
            )

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # مراقبة منشورات جميع القنوات المضافة
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, watch_channels))

    print("Application started")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == '__main__':
    asyncio.run(main())
