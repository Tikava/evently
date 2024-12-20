from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.utils.translation import LANGUAGES, get_translation
from app.database.db import Session
from app.database.models import User


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    main_menu_id = context.user_data["main_menu"]
    keyboard = [[InlineKeyboardButton(LANGUAGES[code], callback_data=code) for code in LANGUAGES],
                [InlineKeyboardButton(get_translation(context.user_data, 'back'), callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(get_translation(context.user_data, 'available_languages'),
                                        chat_id=update.effective_user.id, message_id=main_menu_id,
                                        reply_markup=reply_markup)


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(get_translation(context.user_data, 'language_selected'), show_alert=True)
    with Session() as session:
        session.query(User).filter_by(id=update.effective_user.id).update({'preferred_language': query.data})
        session.commit()
    context.user_data['language'] = query.data
