import os
import re
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# لازم تحط التوكن كـ Variable في Railway
TOKEN = os.getenv("6356842380:AAE-npnKtBRLiUS0o3HgxowDjxi7NnGuCec")

# استخراج رابط تويتر
def extract_twitter_url(text: str):
    m = re.search(r"https?://(www\.)?(twitter|x)\.com/\S+", text)
    return m.group(0) if m else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ارسل رابط تويتر (X) وسأعطيك خيارات التحميل 🎥"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    url = extract_twitter_url(text)

    if not url:
        await update.message.reply_text("ارسل رابط تويتر صحيح.")
        return

    keyboard = [
        [
            InlineKeyboardButton("🔥 افضل جودة", callback_data=f"best|{url}"),
            InlineKeyboardButton("⚖️ متوسطة", callback_data=f"mid|{url}"),
            InlineKeyboardButton("💾 ضعيفة", callback_data=f"low|{url}")
        ]
    ]

    await update.message.reply_text(
        "اختر جودة الفيديو:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality, url = query.data.split("|", 1)
    await query.edit_message_text("⏬ جاري التحميل، انتظر قليلاً...")

    ydl_opts = {
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4"
    }

    if quality == "best":
        ydl_opts["format"] = "bestvideo+bestaudio/best"
    elif quality == "mid":
        ydl_opts["format"] = "bestvideo[height<=720]+bestaudio/best"
    else:
        ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await context.bot.send_video(
            chat_id=query.message.chat_id,
            video=open(file_path, "rb"),
            caption="✅ تم التحميل"
        )

    except Exception as e:
        await query.edit_message_text(f"❌ خطأ:\n{e}")

async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot started...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
