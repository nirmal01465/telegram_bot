import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CHANNEL_ID = -1002455577454  # Your private channel ID

# Help command text
help_text = "🛠️ *Available Commands:*\n1. /get_movie - Get a personalized movie recommendation based on your choice!\n2. /search_movie - Search for a movie by title.\n3. /help - Show this help message.\n\nIf you need assistance, just ask!"

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(
        f'👋 Welcome {user_first_name}! I am Niirmal, a bot. How can I help you today?'
    )
    await show_main_menu(update)

# Show main menu with command buttons
async def show_main_menu(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Get Movie Recommendation", callback_data='get_movie')],
        [InlineKeyboardButton("Search Movie", callback_data='search_movie')],
        [InlineKeyboardButton("Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose an option:', reply_markup=reply_markup)

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Callback for button selection
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    logger.info("Button clicked: %s", query.data)  # Log button press for debugging

    if query.data == 'get_movie':
        response = "🎬 Here is a movie recommendation for you: *Inception*! Enjoy the show! 🍿"
        await query.edit_message_text(text=response, parse_mode='Markdown')
    elif query.data == 'search_movie':
        await query.edit_message_text(text='🔍 Please enter the name of the movie you want to search for:')
        context.user_data['searching'] = True  # Set the flag that user is searching
    elif query.data == 'help':
        await help_command(update, context)
    else:
        await query.edit_message_text(text="Invalid selection. Please try again.")

# Handle text messages (for searching movies)
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('searching'):
        movie_name = update.message.text
        await search_in_channel(movie_name, update, context)
        context.user_data['searching'] = False  # Reset the state after the search
    else:
        await update.message.reply_text("Please choose an option from the menu or type /help.")

# Search the channel for messages matching the movie title
async def search_in_channel(movie_name: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        matched_messages = []
        
        logger.info(f"Attempting to access channel with ID: {CHANNEL_ID}")
        chat = await context.bot.get_chat(CHANNEL_ID)  # Verify chat access
        
        # Fetch messages
        async for message in context.bot.get_chat_history(chat_id=CHANNEL_ID, limit=100):
            if message.text and movie_name.lower() in message.text.lower():
                matched_messages.append(message.text)
                if len(matched_messages) == 3:
                    break  # Only show the first 3 matches
        
        if matched_messages:
            response = "\n\n".join(matched_messages)
            await update.message.reply_text(f"🎬 Here are the top 3 results for *{movie_name}*:\n\n{response}", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"Sorry, no results found for *{movie_name}*.", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error fetching messages from the channel: {e}")
        await update.message.reply_text(f"An error occurred while searching for the movie: {str(e)}")

# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    application = ApplicationBuilder().token("7646833841:AAGlpIsKi0M0xwU9EHZ0z4f-nUKOy32zb08").build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
