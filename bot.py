import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
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

    # Create a list of quality levels with links as inline keyboard buttons
    quality_buttons = []
    for format in formats:
        if format.get('height'):
            quality_buttons.append([telegram.InlineKeyboardButton(f"{format['height']}p", callback_data=format['format_id'])])

    # Create an InlineKeyboardMarkup with the quality buttons
    reply_markup = telegram.InlineKeyboardMarkup(quality_buttons)

    # Prompt the user to select a quality level using the inline keyboard
    update.message.reply_text("Select a quality level:", reply_markup=reply_markup)

    # Store the available quality levels in the context for the next state
    context.user_data["quality_buttons"] = quality_buttons

    # Return QUALITY_SELECTION state to handle the user's response
    return QUALITY_SELECTION

def handle_quality_selection(update, context):
    # Get the user's selected quality level
    selected_quality = update.callback_query.data

    # Get the available quality buttons from the context
    quality_buttons = context.user_data.get("quality_buttons", [])

    # Find the selected quality in the buttons list to retrieve the corresponding URL
    selected_url = None
    for button_row in quality_buttons:
        for button in button_row:
            if button.callback_data == selected_quality:
                selected_url = button.text

    if selected_url:
        # Extract the dash manifest URL for the selected format
        ydl_opts = {
            "format": selected_quality,
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
        update.message.reply_text(f"Dash manifest URL ({selected_url}): {dash_manifest_url}")
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

    # Add a callback query handler to handle inline keyboard button clicks
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_quality_selection))

    # Create a conversation handler to handle the quality selection flow
    quality_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [CallbackQueryHandler(handle_quality_selection)]
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
