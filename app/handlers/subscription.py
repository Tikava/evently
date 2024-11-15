from telegram import Update
from telegram.ext import ContextTypes

from app.utils.helpers import subscription_required
from app.utils.translation import get_translation


@subscription_required
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        get_translation(context.user_data, 'subscribe')
    )