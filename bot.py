import os
from threading import Thread
from flask import Flask
from pytube import YouTube
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ------------------------ CONFIG ------------------------
TOKEN = os.environ.get("TOKEN")  # Heroku/Railway environment variable
CHANNEL_MESSAGE = "\n\nPlease join our channel @lifeonbots"
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB limit

# ------------------------ FLASK 24/7 ------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def keep_alive():
    t = Thread(target=app.run, kwargs={"host":"0.0.0.0","port":8080})
    t.start()

# ------------------------ USER DATA ------------------------
user_data = {}  # Store YouTube objects per user

# ------------------------ COMMANDS ------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a YouTube link and I will let you choose Video/Audio and Quality."
        + CHANNEL_MESSAGE
    )

# ------------------------ HANDLE LINK ------------------------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    try:
        yt = YouTube(url)
        user_data[update.effective_user.id] = {"yt": yt}

        keyboard = [
            [InlineKeyboardButton("Video", callback_data="video")],
            [InlineKeyboardButton("Audio", callback_data="audio")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Choose download type:" + CHANNEL_MESSAGE, reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text(f"Invalid YouTube link.\nError: {e}" + CHANNEL_MESSAGE)

# ------------------------ BUTTON HANDLER ------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.edit_message_text("Session expired. Please send the link again." + CHANNEL_MESSAGE)
        return

    yt = user_data[user_id]["yt"]

    # ---------------- VIDEO CHOOSE ----------------
    if query.data == "video":
        streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
        keyboard = []
        added_resolutions = set()
        for s in streams:
            if s.resolution not in added_resolutions:
                keyboard.append([InlineKeyboardButton(s.resolution, callback_data=f"video_{s.itag}")])
                added_resolutions.add(s.resolution)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose video quality:" + CHANNEL_MESSAGE, reply_markup=reply_markup)

    # ---------------- AUDIO CHOOSE ----------------
    elif query.data == "audio":
        streams = yt.streams.filter(only_audio=True).order_by("abr").desc()
        keyboard = []
        for s in streams:
            keyboard.append([InlineKeyboardButton(f"{s.abr}", callback_data=f"audio_{s.itag}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose audio quality:" + CHANNEL_MESSAGE, reply_markup=reply_markup)

    # ---------------- DOWNLOAD VIDEO ----------------
    elif query.data.startswith("video_"):
        itag = int(query.data.split("_")[1])
        stream = yt.streams.get_by_itag(itag)
        await download_and_send(query, stream, "video")

    # ---------------- DOWNLOAD AUDIO ----------------
    elif query.data.startswith("audio_"):
        itag = int(query.data.split("_")[1])
        stream = yt.streams.get_by_itag(itag)
        await download_and_send(query, stream, "audio")

# ------------------------ DOWNLOAD FUNCTION ------------------------
async def download_and_send(query, stream, dtype):
    msg = await query.edit_message_text(f"Downloading {dtype}... ⏳" + CHANNEL_MESSAGE)
    try:
        out_file = stream.download()
        # ---------------- CHECK FILE SIZE ----------------
        if os.path.getsize(out_file) > MAX_FILE_SIZE:
            await msg.edit_text(f"{dtype.capitalize()} too large (>2GB). Cannot send via Telegram." + CHANNEL_MESSAGE)
        else:
            await query.message.reply_document(document=InputFile(out_file), filename=os.path.basename(out_file))
            await msg.edit_text(f"{dtype.capitalize()} sent successfully!" + CHANNEL_MESSAGE)
        os.remove(out_file)
    except Exception as e:
        await msg.edit_message_text(f"Failed to download {dtype}.\nError: {e}" + CHANNEL_MESSAGE)
    finally:
        if query.from_user.id in user_data:
            del user_data[query.from_user.id]

# ------------------------ MAIN FUNCTION ------------------------
def main():
    keep_alive()  # Flask 24/7 server
    app_telegram = ApplicationBuilder().token(TOKEN).build()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app_telegram.run_polling()

if __name__ == "__main__":
    main()
