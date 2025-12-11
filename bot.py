from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp
import os

TOKEN = "8049358854:AAG9PfWtuNfXkLiEG_6Sqrmta9MCqvC3tOU"

def start(update, context):
    update.message.reply_text(
        "YouTube link bhejo 🔗\nPhir quality choose karo 🎥🎶"
    )

def ask_quality(update, context):
    url = update.message.text.strip()

    if "http" not in url:
        update.message.reply_text("❌ Valid YouTube link bhejo.")
        return

    context.user_data['url'] = url

    keyboard = [
        [InlineKeyboardButton("144p", callback_data="144"),
         InlineKeyboardButton("240p", callback_data="240")],
        [InlineKeyboardButton("360p", callback_data="360"),
         InlineKeyboardButton("480p", callback_data="480")],
        [InlineKeyboardButton("720p HD", callback_data="720"),
         InlineKeyboardButton("1080p Full HD", callback_data="1080")],
        [InlineKeyboardButton("🎵 Audio MP3", callback_data="audio")]
    ]

    update.message.reply_text(
        "Quality choose karo 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def button(update, context):
    query = update.callback_query
    quality = query.data
    url = context.user_data.get("url")

    query.answer()
    query.edit_message_text("⏳ Download ho raha hai...")

    if quality == "audio":
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        file_path = "audio.mp3"
    else:
        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
        }
        file_path = "video.mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if quality == "audio":
            query.message.reply_audio(open(file_path, "rb"))
        else:
            query.message.reply_video(open(file_path, "rb"))

        os.remove(file_path)

    except Exception as e:
        query.message.reply_text("❌ Error! Link sahi hai ya video private to nahi?")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ask_quality))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
