from telegram import Update
from telegram.ext import ContextTypes

from utils.helpers import subscription_required
from utils.translation import get_translation


@subscription_required
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        get_translation(context.user_data, 'subscribe')
    )