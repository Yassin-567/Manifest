import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler, InlineQueryResultArticle, InputTextMessageContent
import yt_dlp

# Replace this with your bot's token
bot_token = "5987250865:AAHjt2KwXxLXg-szVMmfnfWdG6UA1hcgmwI"

# Define the states used in the conversation flow
QUALITY_SELECTION = 0

def start(update, context):
    update.message.reply_text("Welcome! Send me a YouTube link of any video or live stream.")

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

    # Prompt the user to select a quality level
    quality_levels = [f"{format['height']}p" for format in formats if format.get('height')]
    prompt = "Select a quality level:\n\n" + "\n".join([f"/select_{i+1} {level}" for i, level in enumerate(quality_levels)])
    update.message.reply_text(prompt)

    # Return to the main event loop and wait for the user's response
    return QUALITY_SELECTION

def handle_quality_selection(update, context):
    # Get the selected quality level
    selected_quality = update.message.text.split("_")[1]

    # Get the YouTube live stream URL from the context
    live_stream_url = context.user_data['live_stream_url']

    # Create a yt_dlp instance and set the options to extract the dash manifest URL
    ydl_opts = {
        "format": selected_quality,
        "forcejson": True,
        "simulate": True,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(live_stream_url, download=False)
        dash_manifest_url = info_dict.get("url")

    # Send the dash manifest URL back to the user
    update.message.reply_text(f"Dash manifest URL ({selected_quality}): {dash_manifest_url}")

    # End the conversation
    return ConversationHandler.END

def inline_quality_selection(update, context):
    query = update.inline_query.query

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
        info_dict = ydl.extract_info(query, download=False)
        formats = info_dict.get("formats")

    results = []
    for i, format in enumerate(formats):
        if format.get('height'):
            quality_level = f"{format['height']}p"
            result_content = InputTextMessageContent(f"/select_{i+1}")
            result = InlineQueryResultArticle(
                id=str(i),
                title=quality_level,
                input_message_content=result_content,
            )
            results.append(result)

    update.inline_query.answer(results)

# Create an instance of the Telegram bot
bot = telegram.Bot(token=bot_token)

# Create an instance of the Telegram updater and attach the bot to it
updater = Updater(token=bot_token, use_context=True)

# Create a conversation handler to handle the quality selection flow
quality_selection_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.text & ~Filters.command, get_dash_manifest_url)],
    states={
        QUALITY_SELECTION: [MessageHandler(Filters.command, handle_quality_selection)]
    },
    fallbacks=[],
    allow_reentry=True
)

# Add the quality selection handler to the updater
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(quality_selection_handler)
updater.dispatcher.add_handler(InlineQueryHandler(inline_quality_selection))

# Start the bot
updater.start_polling()
updater.idle()
