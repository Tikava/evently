import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.db import Session
from models.base import Event
from ai.generation import send_message
from ai.models import BaseModel
from utils.helpers import search_places
from utils.translation import get_translation

BASE_MODEL = BaseModel().get_model()


async def save_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer(text=get_translation(context.user_data, 'event_saved'), show_alert=True)
    
    with Session() as session:
        session.add(Event(text=update.effective_message.text, user_id=update.effective_user.id))
        session.commit()

        
async def related_places_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    
    keywords = context.user_data.get('event_keywords', [])
    places = search_places(keywords)
    
    if not places:
        await query.answer(get_translation(context.user_data, 'no_places'), show_alert=True)  
        return
    
    result = ""
    for place in places:
        result += f"[• {place['name']}](https://2gis.com/geo/{place['id']})\n"
    
    related_places_message_id = context.user_data.get('related_places', None)
    if related_places_message_id:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=related_places_message_id, text=result, parse_mode='Markdown')
    else: 
        message = await context.bot.send_message(update.effective_chat.id, result, parse_mode='Markdown')
        context.user_data['related_places'] = message.id

        
async def try_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    #message = update.message
    
    if 'event_plan' in context.user_data and context.user_data['event_plan'] is not None:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['event_plan'])
        context.user_data['event_plan'] = None
        
    if 'related_places' in context.user_data and context.user_data['related_places'] is not None:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['related_places'])
        context.user_data['related_places'] = None
    
    if 'error_message' in context.user_data and context.user_data['error_message'] is not None:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['error_message'])
        context.user_data['error_message'] = None
    
    message = await context.bot.send_message(update.effective_chat.id, get_translation(context.user_data, 'generating_again_message'))
    context.user_data['event_plan'] = message.id

    event_plan = send_message(BASE_MODEL, update.effective_user.id, get_translation(context.user_data, 'to_bot_generate_again'))
    
    #context.user_data['event_keywords'] = event_plan_json['event_keywords']
    
    # Setting up the inline keyboard
    keyboard = [[InlineKeyboardButton(get_translation(context.user_data, 'save'), callback_data="save"), InlineKeyboardButton(get_translation(context.user_data, 'related_places'), callback_data="related_places"), InlineKeyboardButton(get_translation(context.user_data, 'generate_again'), callback_data="try_again")], [InlineKeyboardButton(get_translation(context.user_data, 'my_profile'), callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
        
    # Formatting the event plan
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"<b>\1</b>"
    # plan = f"""**{get_translation(context.user_data, 'event_name')}**: {event_plan_json['event_name']}\n\n**{get_translation(context.user_data, 'event_overview')}**: {event_plan_json['event_overview']}\n\n**{get_translation(context.user_data, 'event_plan')}**: {event_plan_json['detailed_event_plan']}\n\n"""
    formatted_plan = re.sub(pattern, replacement, event_plan).replace("* ", '• ')
    
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.id, text=formatted_plan, parse_mode='HTML', reply_markup=reply_markup)
