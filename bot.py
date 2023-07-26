import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import yt_dlp

# Replace this with your bot's token
bot_token = "6266356161:AAEd7RPG1NnYlYr6rDikURVDzZGHtyozeA8"

# Define the states used in the conversation flow
QUALITY_SELECTION, GET_VIDEO_URL = range(2)

def start(update: telegram.Update, context: CallbackContext):
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

def get_dash_manifest_url_from_youtube(video_url):
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            dash_manifest_url = info['url']
            return dash_manifest_url
    except Exception as e:
        print("Error fetching Dash Manifest URL:", str(e))
        return None

def get_dash_manifest_url(update: telegram.Update, context: CallbackContext):
    """Handler function for the YouTube video link input"""
    video_url = update.message.text

    # You can fetch the Dash Manifest URL using the provided function
    dash_manifest_url = get_dash_manifest_url_from_youtube(video_url)

    if dash_manifest_url:
        # Save the Dash Manifest URL to the context for later use
        context.user_data['dash_manifest_url'] = dash_manifest_url

        # Move to the QUALITY_SELECTION state and ask the user to select the desired quality
        update.message.reply_text("Select your desired quality and enjoy ✨", reply_markup=ReplyKeyboardMarkup([['/27p', '/45p', '/90p'], ['/144p', '/240p', '/360p'], ['/480p', '/720p', '/1080p']], resize_keyboard=True, one_time_keyboard=True))

        return QUALITY_SELECTION
    else:
        update.message.reply_text("Sorry, I couldn't fetch the Dash Manifest URL for the provided YouTube video link.")
        return ConversationHandler.END

def select_quality(update: telegram.Update, context: CallbackContext):
    """Handler function for the quality selection"""
    selected_quality = update.message.text

    # Get the saved Dash Manifest URL from the context
    dash_manifest_url = context.user_data.get('dash_manifest_url')

    # You can use the selected quality and the saved Dash Manifest URL to perform further actions
    # For this example, I'll just reply with the selected quality and the Dash Manifest URL and end the conversation.
    update.message.reply_text(f"Enjoy your video in {selected_quality} ✨\nManifest URL: {dash_manifest_url}", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

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
        entry_points=[MessageHandler(Filters.regex(r".*youtu(?:be\.com|\.be).*"), get_dash_manifest_url)],
        states={
            QUALITY_SELECTION: [MessageHandler(Filters.regex(r"^(\/[1-9][0-9]*p)$"), select_quality)]
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
