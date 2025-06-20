import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from config import TELEGRAM_BOT_TOKEN, SUPPORTED_LANGUAGES
from tmdb_api import TMDbAPI

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize TMDb API
tmdb = TMDbAPI()

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    welcome_message = (
        "👋 Welcome to TMDb Poster Bot!\n\n"
        "I can help you find posters and information about movies and TV shows.\n\n"
        "Try searching with: /tmdb <movie or show name>\n"
        "or: /trndb <movie or show name>\n\n"
        "For example: /tmdb Inception"
    )
    update.message.reply_text(welcome_message)

def tmdb_search(update: Update, context: CallbackContext) -> None:
    """Handle the /tmdb command to search for movies and TV shows."""
    if not context.args:
        update.message.reply_text("Please provide a movie or TV show name. Example: /tmdb Inception")
        return
    
    query = ' '.join(context.args)
    update.message.reply_text(f"🔍 Searching for '{query}'...")
    
    # Search TMDb API
    results = tmdb.search_multi(query)
    
    if not results or not results.get('results'):
        update.message.reply_text(f"No results found for '{query}'. Please try another search.")
        return
    
    # Filter results to only include movies and TV shows (not people)
    media_results = [item for item in results['results'] if item['media_type'] in ['movie', 'tv']][:10]
    
    if not media_results:
        update.message.reply_text(f"No movies or TV shows found for '{query}'. Please try another search.")
        return
    
    # Create inline keyboard with search results
    keyboard = []
    for item in media_results:
        title = item.get('title', item.get('name', 'Unknown'))
        year = ""
        if item['media_type'] == 'movie' and item.get('release_date'):
            year = f" ({item['release_date'][:4]})"
        elif item['media_type'] == 'tv' and item.get('first_air_date'):
            year = f" ({item['first_air_date'][:4]})"
        
        media_type = "🎬" if item['media_type'] == 'movie' else "📺"
        button_text = f"{media_type} {title}{year}"
        callback_data = f"details_{item['media_type']}_{item['id']}_en-US"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Found {len(media_results)} results for '{query}':", reply_markup=reply_markup)

def handle_details(update: Update, context: CallbackContext) -> None:
    """Handle button press to show media details."""
    query = update.callback_query
    query.answer()
    
    # Parse callback data
    data_parts = query.data.split('_')
    if len(data_parts) < 4 or data_parts[0] != 'details':
        query.edit_message_text("Invalid selection. Please try again.")
        return
    
    _, media_type, media_id, language = data_parts
    
    # Get detailed information
    details = tmdb.get_details(media_type, media_id, language)
    if not details:
        query.edit_message_text("Failed to fetch details. Please try again.")
        return
    
    # Get title and basic info
    title = details.get('title', details.get('name', 'Unknown'))
    
    # Create message with media information
    if media_type == 'movie':
        release_date = details.get('release_date', 'Unknown')
        runtime = details.get('runtime', 0)
        runtime_str = f"{runtime} minutes" if runtime else "Unknown"
        
        info_text = (
            f"🎬 *{title}*\n\n"
            f"📅 Release Date: {release_date}\n"
            f"⏱️ Runtime: {runtime_str}\n"
            f"⭐ Rating: {details.get('vote_average', 'N/A')}/10\n\n"
            f"📝 Overview: {details.get('overview', 'No overview available.')}"
        )
    else:  # TV show
        first_air_date = details.get('first_air_date', 'Unknown')
        seasons = details.get('number_of_seasons', 0)
        episodes = details.get('number_of_episodes', 0)
        
        info_text = (
            f"📺 *{title}*\n\n"
            f"📅 First Air Date: {first_air_date}\n"
            f"🔢 Seasons: {seasons}\n"
            f"📚 Episodes: {episodes}\n"
            f"⭐ Rating: {details.get('vote_average', 'N/A')}/10\n\n"
            f"📝 Overview: {details.get('overview', 'No overview available.')}"
        )
    
    # Create keyboard for images and language options
    keyboard = []
    
    # Current language name
    current_lang_name = next((name for name, code in SUPPORTED_LANGUAGES.items() if code == language), "English")
    
    # Poster button (if available) - Portrait (High-Res by default)
    if details.get('poster_path'):
        poster_url = tmdb.get_poster_url(details['poster_path'], 'original')  # High-Res by default
        keyboard.append([
            InlineKeyboardButton(f"🖼️ Portrait Poster ({current_lang_name})", url=poster_url)
        ])
    else:
        keyboard.append([InlineKeyboardButton("❌ No Portrait Poster Available", callback_data="no_action")])
    
    # Backdrop button (if available) - Landscape (High-Res by default)
    backdrops = details.get('images', {}).get('backdrops', [])
    if details.get('backdrop_path'):
        backdrop_url = tmdb.get_backdrop_url(details['backdrop_path'], 'original')  # High-Res by default
        keyboard.append([
            InlineKeyboardButton(f"🌆 Landscape Poster ({current_lang_name})", url=backdrop_url)
        ])
    elif backdrops:
        # If main backdrop not available but there are backdrops in images
        backdrop = backdrops[0]
        backdrop_url = tmdb.get_backdrop_url(backdrop['file_path'], 'original')  # High-Res by default
        keyboard.append([
            InlineKeyboardButton(f"🌆 Landscape Poster ({current_lang_name})", url=backdrop_url)
        ])
    else:
        keyboard.append([InlineKeyboardButton("❌ No Landscape Poster Available", callback_data="no_action")])
        
    # View All Backdrops button (if there are multiple backdrops)
    if len(backdrops) > 1:
        keyboard.append([
            InlineKeyboardButton(f"🖼️ View All {len(backdrops)} Backdrops", callback_data=f"backdrops_{media_type}_{media_id}_{language}")
        ])
        
    # Logo button (if available) - High-Res by default
    logos = details.get('images', {}).get('logos', [])
    logos = [logo for logo in logos if logo.get('iso_639_1') == language[:2] or not logo.get('iso_639_1')]
    
    if logos:
        logo = logos[0]  # Get the first logo for the current language or without language specification
        logo_url = tmdb.get_logo_url(logo['file_path'], 'original')  # High-Res by default
        keyboard.append([
            InlineKeyboardButton(f"🎥 Logo ({current_lang_name})", url=logo_url)
        ])
    else:
        keyboard.append([InlineKeyboardButton("❌ No Logo Available", callback_data="no_action")])
        
    # Send All Images button
    keyboard.append([
        InlineKeyboardButton("📦 Send All Images", callback_data=f"send_all_{media_type}_{media_id}_{language}")
    ])
    
    # Language options
    lang_buttons = []
    for lang_name, lang_code in SUPPORTED_LANGUAGES.items():
        if lang_code != language:
            lang_buttons.append(
                InlineKeyboardButton(
                    f"{lang_name}", 
                    callback_data=f"details_{media_type}_{media_id}_{lang_code}"
                )
            )
    
    # Add language buttons in groups of 3
    for i in range(0, len(lang_buttons), 3):
        keyboard.append(lang_buttons[i:i+3])
    
    # Back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Search", callback_data=f"back_to_search")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send or edit message with details
    try:
        query.edit_message_text(
            text=info_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        # If editing fails (e.g., due to identical content), try without parse_mode
        query.edit_message_text(
            text=info_text,
            reply_markup=reply_markup
        )

def handle_back_to_search(update: Update, context: CallbackContext) -> None:
    """Handle the back button to return to search."""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        "Please use /tmdb <movie or show name> to search again.",
    )

def handle_no_action(update: Update, context: CallbackContext) -> None:
    """Handle buttons that should not perform any action."""
    query = update.callback_query
    query.answer("No action available")

def handle_send_all_images(update: Update, context: CallbackContext) -> None:
    """Handle the send all images button."""
    query = update.callback_query
    query.answer("Preparing all images...")
    
    # Parse callback data
    data_parts = query.data.split('_')
    if len(data_parts) < 4 or data_parts[0] != 'send':
        query.edit_message_text("Invalid selection. Please try again.")
        return
    
    _, all, media_type, media_id, language = data_parts
    
    # Get detailed information
    details = tmdb.get_details(media_type, media_id, language)
    if not details:
        query.edit_message_text("Failed to fetch details. Please try again.")
        return
    
    # Get title
    title = details.get('title', details.get('name', 'Unknown'))
    current_lang_name = next((name for name, code in SUPPORTED_LANGUAGES.items() if code == language), "English")
    
    # Create message with all image links
    message = f"🎬 *{title}* - All Images ({current_lang_name})\n\n"
    
    # Add poster links (high-res by default)
    if details.get('poster_path'):
        poster_url = tmdb.get_poster_url(details['poster_path'], 'original')  # High-res by default
        message += f"🖼️ *Portrait Poster*:\n{poster_url}\n\n"
    
    # Add backdrop links (high-res by default)
    if details.get('backdrop_path'):
        backdrop_url = tmdb.get_backdrop_url(details['backdrop_path'], 'original')  # High-res by default
        message += f"🌆 *Landscape Poster*:\n{backdrop_url}\n\n"
    elif details.get('images', {}).get('backdrops'):
        backdrop = details['images']['backdrops'][0]
        backdrop_url = tmdb.get_backdrop_url(backdrop['file_path'], 'original')  # High-res by default
        message += f"🌆 *Landscape Poster*:\n{backdrop_url}\n\n"
    
    # Add logo links (high-res by default)
    logos = details.get('images', {}).get('logos', [])
    logos = [logo for logo in logos if logo.get('iso_639_1') == language[:2] or not logo.get('iso_639_1')]
    
    if logos:
        logo = logos[0]
        logo_url = tmdb.get_logo_url(logo['file_path'], 'original')  # High-res by default
        message += f"🎬 *Logo*:\n{logo_url}\n\n"
    
    # Add buttons for backdrops and back
    keyboard = []
    
    # Add view all backdrops button if there are multiple backdrops
    backdrops = details.get('images', {}).get('backdrops', [])
    if len(backdrops) > 1:
        keyboard.append([
            InlineKeyboardButton(f"🖼️ View All {len(backdrops)} Backdrops", callback_data=f"backdrops_{media_type}_{media_id}_{language}")
        ])
    
    # Back button
    keyboard.append([
        InlineKeyboardButton("🔙 Back to Details", callback_data=f"details_{media_type}_{media_id}_{language}")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with all image links
    try:
        query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True  # Disable preview to avoid showing just one image
        )
    except Exception as e:
        logger.error(f"Error sending all images: {e}")
        query.edit_message_text(
            text="Failed to send all images. Please try again.",
            reply_markup=reply_markup
        )

def handle_backdrops(update: Update, context: CallbackContext) -> None:
    """Handle the view all backdrops button."""
    query = update.callback_query
    query.answer("Loading all backdrops...")
    
    # Parse callback data
    data_parts = query.data.split('_')
    if len(data_parts) < 4 or data_parts[0] != 'backdrops':
        query.edit_message_text("Invalid selection. Please try again.")
        return
    
    _, media_type, media_id, language = data_parts
    
    # Get detailed information
    details = tmdb.get_details(media_type, media_id, language)
    if not details:
        query.edit_message_text("Failed to fetch details. Please try again.")
        return
    
    # Get title
    title = details.get('title', details.get('name', 'Unknown'))
    
    # Get all backdrops
    backdrops = details.get('images', {}).get('backdrops', [])
    if not backdrops:
        query.edit_message_text(f"No backdrops found for {title}.")
        return
    
    # Group backdrops by language
    backdrops_by_lang = {}
    for backdrop in backdrops:
        lang_code = backdrop.get('iso_639_1') or 'null'  # Use 'null' for backdrops without language
        if lang_code not in backdrops_by_lang:
            backdrops_by_lang[lang_code] = []
        backdrops_by_lang[lang_code].append(backdrop)
    
    # Create message with backdrop count by language
    message = f"🌆 *{title}* - All Backdrops\n\n"
    
    # Create keyboard with language options for backdrops
    keyboard = []
    
    # Add buttons for each language with backdrops
    for lang_code, lang_backdrops in backdrops_by_lang.items():
        if lang_code == 'null':
            lang_name = "No Language"
        else:
            lang_name = next((name for name, code in SUPPORTED_LANGUAGES.items() if code.startswith(lang_code)), lang_code)
        
        # Button to view all backdrops in this language
        keyboard.append([
            InlineKeyboardButton(
                f"{lang_name} ({len(lang_backdrops)} backdrops)", 
                callback_data=f"lang_backdrops_{media_type}_{media_id}_{language}_{lang_code}"
            )
        ])
        
        # Add to message
        message += f"• {lang_name}: {len(lang_backdrops)} backdrops\n"
    
    # Back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Details", callback_data=f"details_{media_type}_{media_id}_{language}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with backdrop language options
    try:
        query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing backdrops: {e}")
        query.edit_message_text(
            text="Failed to show backdrops. Please try again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Details", callback_data=f"details_{media_type}_{media_id}_{language}")
            ]])
        )

def handle_lang_backdrops(update: Update, context: CallbackContext) -> None:
    """Handle showing backdrops for a specific language."""
    query = update.callback_query
    query.answer("Loading backdrops...")
    
    # Parse callback data
    data_parts = query.data.split('_')
    if len(data_parts) < 6 or data_parts[0] != 'lang':
        query.edit_message_text("Invalid selection. Please try again.")
        return
    
    _, _, media_type, media_id, base_language, backdrop_lang_code = data_parts
    
    # Get detailed information
    details = tmdb.get_details(media_type, media_id, base_language)
    if not details:
        query.edit_message_text("Failed to fetch details. Please try again.")
        return
    
    # Get title
    title = details.get('title', details.get('name', 'Unknown'))
    
    # Get all backdrops for the selected language
    all_backdrops = details.get('images', {}).get('backdrops', [])
    if backdrop_lang_code == 'null':
        backdrops = [b for b in all_backdrops if not b.get('iso_639_1')]
        lang_name = "No Language"
    else:
        backdrops = [b for b in all_backdrops if b.get('iso_639_1') == backdrop_lang_code]
        lang_name = next((name for name, code in SUPPORTED_LANGUAGES.items() if code.startswith(backdrop_lang_code)), backdrop_lang_code)
    
    if not backdrops:
        query.edit_message_text(f"No backdrops found for {title} in {lang_name}.")
        return
    
    # Create message with all backdrop links
    message = f"🌆 *{title}* - {lang_name} Backdrops ({len(backdrops)})\n\n"
    
    # Add all backdrop links (high-res by default)
    for i, backdrop in enumerate(backdrops[:10]):  # Limit to 10 backdrops to avoid message size limits
        backdrop_url = tmdb.get_backdrop_url(backdrop['file_path'], 'original')  # High-res by default
        message += f"*Backdrop {i+1}*:\n{backdrop_url}\n\n"
    
    # Note if there are more backdrops
    if len(backdrops) > 10:
        message += f"_Note: Showing 10 of {len(backdrops)} backdrops_\n\n"
    
    # Back buttons
    keyboard = [
        [InlineKeyboardButton("🔙 Back to All Backdrops", callback_data=f"backdrops_{media_type}_{media_id}_{base_language}")],
        [InlineKeyboardButton("🔙 Back to Details", callback_data=f"details_{media_type}_{media_id}_{base_language}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with backdrop links
    try:
        query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True  # Disable preview to avoid showing just one image
        )
    except Exception as e:
        logger.error(f"Error showing language backdrops: {e}")
        query.edit_message_text(
            text="Failed to show backdrops. Please try again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Details", callback_data=f"details_{media_type}_{media_id}_{base_language}")
            ]])
        )

def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Route callback queries to appropriate handlers."""
    query = update.callback_query
    data = query.data
    
    if data.startswith('details_'):
        handle_details(update, context)
    elif data.startswith('send_all_'):
        handle_send_all_images(update, context)
    elif data.startswith('backdrops_'):
        handle_backdrops(update, context)
    elif data.startswith('lang_backdrops_'):
        handle_lang_backdrops(update, context)
    elif data == 'back_to_search':
        handle_back_to_search(update, context)
    elif data == 'no_action':
        handle_no_action(update, context)
    else:
        query.answer("Unknown action")

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("tmdb", tmdb_search))
    # Also register the alternative command as mentioned in requirements
    dispatcher.add_handler(CommandHandler("trndb", tmdb_search))
    
    # Register callback query handler
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
    else:
        main()