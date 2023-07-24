import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler, InlineQueryResultArticle, InputTextMessageContent
import yt_dlp

# Replace this with your bot's token
bot_token = "5987250865:AAHjt2KwXxLXg-szVMmfnfWdG6UA1hcgmwI"

# Define the states used in the conversation flow
QUALITY_SELECTION = 0

def start(update, context):
    update.message.reply_text("Welcome! Please send me a YouTube link of any video or live stream.")

def get_dash_manifest_url(update, context):
    # Get the YouTube live stream URL from the message sent to the bot
    live_stream_url = update.message.text

    # Create a yt_dlp instance and set the options to extract the formats
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

    # Prompt the user to select a quality level with inline commands
    quality_levels = [f"{format['height']}p" for format in formats if format.get('height')]
    results = [InlineQueryResultArticle(id=str(i), title=level, input_message_content=InputTextMessageContent(live_stream_url)) for i, level in enumerate(quality_levels)]
    update.message.reply_text("Select a quality level:", reply_markup=telegram.InlineKeyboardMarkup.from_column(results))

    # Return the QUALITY_SELECTION state
    return QUALITY_SELECTION

def handle_quality_selection(update, context):
    # Get the chosen quality level
    selected_index = int(update.callback_query.data)
    live_stream_url = update.callback_query.message.text
    ydl_opts = {"format": f"{selected_index}+best", "forcejson": True}

    # Extract the dash manifest URL for the selected format
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(live_stream_url, download=False)
        dash_manifest_url = info_dict.get("url")

    # Send the dash manifest URL back to the user
    update.callback_query.message.reply_text(f"Dash manifest URL ({dash_manifest_url}): {dash_manifest_url}")

    # End the conversation
    return ConversationHandler.END

def main():
    # Create an instance of the Telegram bot
    bot = telegram.Bot(token=bot_token)

    # Create an instance of the Telegram updater and attach the bot to it
    updater = Updater(token=bot_token, use_context=True)

    # Create a conversation handler to handle the quality selection flow
    quality_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [CallbackQueryHandler(handle_quality_selection)]
        },
        fallbacks=[]
    )

    # Add the quality selection handler to the updater
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(quality_selection_handler)
    updater.dispatcher.add_handler(InlineQueryHandler(get_dash_manifest_url))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
