import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Replace this with your bot's token
bot_token = "5987250865:AAHjt2KwXxLXg-szVMmfnfWdG6UA1hcgmwI"

# Define the states used in the conversation flow
QUALITY_SELECTION = 0

def start(update, context):
    """Handler function for the /start command"""
    # Define the custom keyboard
    keyboard = [
        [telegram.KeyboardButton('/start')],
        [telegram.KeyboardButton('/help')]
    ]
    # Create a reply markup with the custom keyboard
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    # Send the message with the custom keyboard
    update.message.reply_text("Hello there🙋‍♂️\nSend me any YouTube video link🔗, and wait for the magic to happen🔮...\n\nYou can also use the following commands:", reply_markup=reply_markup)

def get_dash_manifest_url(update, context):
    """Handler function for the /dash_manifest_url command"""

    # Get the YouTube video link from the user
    video_url = update.message.text

    # Get the dash manifest URL for the video
    dash_manifest_url = get_dash_manifest_url_from_youtube(video_url)

    # Send the dash manifest URL to the user
    update.message.reply_text(dash_manifest_url)

def help(update, context):
    """Handler function for the /help command"""
    update.message.reply_text("This is how to use, its super easy😎\n\n1. Send a YouTube video link🔗\n2. Choose your manifest URL desired quality🔢\n3. Use the manifest URL to play the video directly on your TV📺")

def main():
    # Create an instance of the Telegram bot
    bot = telegram.Bot(token=bot_token)

    # Create an instance of the Telegram updater and attach the bot to it
    updater = Updater(token=bot_token, use_context=True)

    # Add a command handler to handle the /start command
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # Add a command handler to handle the /help command
    updater.dispatcher.add_handler(CommandHandler("help", help))

    # Create a conversation handler to handle the quality selection flow
    quality_selection_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+"), get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [MessageHandler(Filters.regex(r"^\/[1-9][0-9]*p$"), get_dash_manifest_url)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    # Add the quality selection handler to the updater
    updater.dispatcher.add_handler(quality_selection_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
