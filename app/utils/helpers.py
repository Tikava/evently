from functools import wraps
from typing import List
import requests
import urllib.parse

from telegram import Update
from telegram.ext import ContextTypes

from app.config import CHANNEL_USERNAME, TWOGIS_API_KEY
from app.utils.translation import get_translation

async def check_subscription_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    status = (await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)).status
    return status != "left"

def subscription_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not await check_subscription_status(update, context):
            await update.message.reply_text(
                get_translation(context.user_data, 'join_channel').format(channel=CHANNEL_USERNAME)
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def search_places(keywords: List[str]) -> List[str]:
    encoded_keywords = urllib.parse.quote_plus(" ".join(keywords))
    URL = f"https://catalog.api.2gis.com/3.0/items?q={encoded_keywords}&key={TWOGIS_API_KEY}"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()  
        json_obj = response.json()
        
        places = json_obj.get('result', {}).get('items', [])
        resulted_obj = [
            {"name": place.get('name'), "id": place.get('id')}
            for place in places
        ]
        return resulted_obj
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []
    except ValueError as e:
        print(f"JSON decoding error: {e}")
        return []