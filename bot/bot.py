import datetime
import io
import json
import logging
import traceback
from logging.handlers import RotatingFileHandler

import httpx
from database import db_client
from lang_validators import vaidate_spanish_word
from mochi import Card, MochiClient, get_deck_by_name
from telegram import BotCommand, InputMediaDocument, Update
from telegram.constants import ParseMode
from telegram.ext import (AIORateLimiter, Application, ApplicationBuilder,
                          CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler)

import config
HTTPX_CLIENT = httpx.AsyncClient()

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    handler = RotatingFileHandler("logs/bot.log", maxBytes=50000000, backupCount=5)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(file_formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

logger = logging.getLogger(__name__)


async def start_handle(update: Update, context: CallbackContext):
    logger.info(
        f"Handling start command. User_id: {update.effective_user.id}. Message: {getattr(update.effective_message, 'text', 'no text')}"
    )


async def add_word(update: Update, context: CallbackContext):
    logger.info(
        f"Handling add_word command. User_id: {update.effective_user.id}. Message: {getattr(update.effective_message, 'text', 'no text')}"
    )
    if 'new_word' not in context.user_data:
        word_pos = vaidate_spanish_word(update.effective_message.text)

        user = db_client.get_user(update.effective_user.id)
        mochi_client = MochiClient(HTTPX_CLIENT, user.mochi_api_key)
        
        # list all decks
        deck_list = await mochi_client.list_all_decks()
        if word_pos == "NOUN":
            deck = get_deck_by_name(deck_list, "Nouns")
        elif word_pos == "VERB":
            deck = get_deck_by_name(deck_list, "Verbs")
        elif word_pos == "ADJ":
            deck = get_deck_by_name(deck_list, "Adj")
        else:
            deck = get_deck_by_name(deck_list, "Phrases")
        new_card = Card(deck)
        new_card.add_field_value("Spanish", update.effective_message.text)
        context.user_data['new_word'] = {'card':new_card, 'api_client': mochi_client}
    else:
        new_card = context.user_data['new_word']['card']
        mochi_client = context.user_data['new_word']['api_client']
        next_field = new_card.get_next_empty_field()
        new_card.add_field_value(next_field.name, update.effective_message.text)

    next_field = new_card.get_next_empty_field()
    if next_field is not None:
        await update.message.reply_text(f"Please enter the next field \"{next_field.name}\" for the word")
    else:
        response = await mochi_client.add_card(new_card)
        if response.status_code != 200:
            await update.message.reply_text(f"Error adding word. Error: {response.text}")
        else:
            await update.message.reply_text("Word added successfully")
        del context.user_data['new_word']
        return

# async def post_init(application: Application):
#     await application.bot.set_my_commands(
#         [
#             BotCommand("/add_user", texts["ru"]["menu_add_user_cmd"]),
#             BotCommand("/happy_bday", texts["ru"]["menu_add_generate_greetings"]),
#             BotCommand("/watchlist", texts["ru"]["menu_watchlist_cmd"]),
#             BotCommand("/settings", texts["ru"]["menu_settings_cmd"]),
#             # BotCommand("/balance", texts["ru"]["menu_add_balance_cmd"]),
#             BotCommand("/help", texts["ru"]["menu_help_cmd"]),
#         ]
#     )

def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token(config.bot_token)  # .token(config.bot_token)
        .concurrent_updates(True)
        # .rate_limiter(AIORateLimiter(max_retries=5))
        # .http_version("1.1")
        # .get_updates_http_version("1.1")
        # .post_init(post_init)
        .concurrent_updates(False)
        .build()
    )
    application.add_handler(CommandHandler("start", start_handle))
    application.add_handler(MessageHandler(None, add_word))
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_bot()

