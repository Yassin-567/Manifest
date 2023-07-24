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

    # Create a list of quality levels
    quality_levels = [f"{format['height']}p" for format in formats if format.get('height')]

    # Prompt the user to select a quality level from the list
    update.message.reply_text("Select a quality level from the list:\n\n" + "\n".join(quality_levels))

    # Store the available quality levels in the context for the next state
    context.user_data["quality_levels"] = quality_levels

    # Return QUALITY_SELECTION state to handle the user's response
    return QUALITY_SELECTION

def handle_quality_selection(update, context):
    # Get the user's selected quality level
    selected_quality = update.message.text

    # Get the available quality levels from the context
    quality_levels = context.user_data.get("quality_levels", [])

    # Check if the selected quality is valid
    if selected_quality in quality_levels:
        # Extract the dash manifest URL for the selected format
        ydl_opts = {
            "format": f"bestvideo[height={selected_quality}]+bestaudio/best",
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
        update.message.reply_text(f"Dash manifest URL ({selected_quality}): {dash_manifest_url}")
    else:
        update.message.reply_text("Invalid quality selection. Please select a quality level from the list.")

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
