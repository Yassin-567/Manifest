import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import yt_dlp

# Replace this with your bot's token
bot_token = "5987250865:AAHjt2KwXxLXg-szVMmfnfWdG6UA1hcgmwI"

# Define the states used in the conversation flow
QUALITY_SELECTION = 0

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
    prompt = "Select a quality level:\n\n" + "\n".join([f"{i+1}. {level}" for i, level in enumerate(quality_levels)])
    update.message.reply_text(prompt)

    # Define a function to handle the user's response
    def handle_quality_selection(update, context):
        # Get the user's selected quality level
        selected_index = int(update.message.text) - 1
        selected_format = formats[selected_index]

        # Extract the dash manifest URL for the selected format
        ydl_opts["format"] = selected_format["format_id"]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(live_stream_url, download=False)
            dash_manifest_url = info_dict.get("url")

        # Send the dash manifest URL back to the user
        update.message.reply_text(f"Dash manifest URL ({selected_format['height']}p): {dash_manifest_url}")

        # End the conversation
        return ConversationHandler.END

    # Add a message handler to listen for the user's response
    selection_handler = MessageHandler(Filters.regex(r"^[1-9][0-9]*$"), handle_quality_selection)
    context.dispatcher.add_handler(selection_handler)

    # Return to the main event loop and wait for the user's response
    return ConversationHandler.END

def main():
    # Create an instance of the Telegram bot
    bot = telegram.Bot(token=bot_token)

    # Create an instance of the Telegram updater and attach the bot to it
    updater = Updater(token=bot_token, use_context=True)

    # Create a conversation handler to handle the quality selection flow
    quality_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+"), get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [MessageHandler(Filters.regex(r"^[1-9][0-9]*$"), get_dash_manifest_url)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    # Add the quality selection handler to the updater
    updater.dispatcher.add_handler(quality_selection_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if name == "main":
    main()