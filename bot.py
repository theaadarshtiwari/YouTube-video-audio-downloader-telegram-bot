from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from pytube import YouTube
import os

# Bot token
TOKEN = "YOUR_BOT_TOKEN_HERE"

# Channel join message
CHANNEL_MESSAGE = "\n\nPlease join our channel @YourChannel"

# Dictionary to store user video info temporarily
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a YouTube link and I will let you choose video/audio and quality."
        + CHANNEL_MESSAGE
    )

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_data:
        await query.edit_message_text("Session expired. Please send the link again." + CHANNEL_MESSAGE)
        return

    yt = user_data[user_id]["yt"]

    if query.data == "video":
        # Show quality options (highest 1080p, 720p, 480p if available)
        streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()
        keyboard = []
        added_resolutions = set()
        for s in streams:
            if s.resolution not in added_resolutions:
                keyboard.append([InlineKeyboardButton(s.resolution, callback_data=f"video_{s.itag}")])
                added_resolutions.add(s.resolution)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose video quality:" + CHANNEL_MESSAGE, reply_markup=reply_markup)
    elif query.data == "audio":
        audio_stream = yt.streams.filter(only_audio=True).first()
        msg = await query.edit_message_text("Downloading audio... ⏳" + CHANNEL_MESSAGE)
        try:
            out_file = audio_stream.download()
            await query.message.reply_document(document=InputFile(out_file), filename=os.path.basename(out_file))
            os.remove(out_file)
            await msg.edit_text("Audio sent successfully!" + CHANNEL_MESSAGE)
        except Exception as e:
            await msg.edit_text(f"Failed to download audio.\nError: {e}" + CHANNEL_MESSAGE)
        del user_data[user_id]
    elif query.data.startswith("video_"):
        itag = int(query.data.split("_")[1])
        stream = yt.streams.get_by_itag(itag)
        msg = await query.edit_message_text("Downloading video... ⏳" + CHANNEL_MESSAGE)
        try:
            out_file = stream.download()
            await query.message.reply_document(document=InputFile(out_file), filename=os.path.basename(out_file))
            os.remove(out_file)
            await msg.edit_text("Video sent successfully!" + CHANNEL_MESSAGE)
        except Exception as e:
            await msg.edit_text(f"Failed to download video.\nError: {e}" + CHANNEL_MESSAGE)
        del user_data[user_id]

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
