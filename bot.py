import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import yt_dlp

# Replace this with your bot's token
bot_token = "5987250865:AAHjt2KwXxLXg-szVMmfnfWdG6UA1hcgmwI"

# Define the states used in the conversation flow
QUALITY_SELECTION = 0

def start(update, context):
    # Send a welcome message with instructions to the user
    update.message.reply_text("Hello, I am ready to extract the manifest URL.\n\nSend me a YouTube video link.")

def get_dash_manifest_url(update, context):
    # Get the YouTube live stream URL from the message sent to the bot
    live_stream_url = update.message.text

    # Create a `yt_dlp` instance and set the options to extract the formats
    ydl_opts = {
        "format": "best",
        "forcejson": True,
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(live_stream_url, download=False)
        formats = info_dict.get("formats")

    # Create a list of quality levels with links as buttons
    quality_buttons = []
    for format in formats:
        if format.get('height'):
            quality_buttons.append(telegram.KeyboardButton(f"{format['height']}p", callback_data=format['format_id']))

    # Create a ReplyKeyboardMarkup with the quality buttons
    reply_markup = telegram.ReplyKeyboardMarkup(
        [quality_buttons],
        one_time_keyboard=True,
        resize_keyboard=True
    )

    # Prompt the user to select a quality level using the buttons
    update.message.reply_text("Select a quality level:", reply_markup=reply_markup)

    # Return QUALITY_SELECTION state to handle the user's response
    return QUALITY_SELECTION

def handle_quality_selection(update, context):
    # Get the user's selected quality level
    selected_format_id = update.callback_query.data

    # Extract the dash manifest URL for the selected format
    ydl_opts = {
        "format": selected_format_id,
        "forcejson": True,
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(update.message.text, download=False)
        dash_manifest_url = info_dict.get("url")

    # Send the dash manifest URL back to the user
    update.message.reply_text(f"Dash manifest URL: {dash_manifest_url}")

    # End the conversation
    return ConversationHandler.END

def main():
    # Create an instance of the Telegram bot
    bot = telegram.Bot(token=bot_token)

    # Create an instance of the Telegram updater and attach the bot to it
    updater = Updater(token=bot_token, use_context=True)

    # Add a command handler to start the conversation
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Create a conversation handler to handle the quality selection flow
    quality_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [MessageHandler(Filters.text & ~Filters.command, handle_quality_selection)]
        },
        fallbacks=[]
    )

    # Add the quality selection handler to the updater
    updater.dispatcher.add_handler(quality_selection_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
