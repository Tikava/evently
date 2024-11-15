from typing import Optional

import jsonpickle
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.future import select

from app.database.db import Session
from app.database.models import User, Chat
from app.utils.helpers import check_subscription_status
from app.utils.translation import get_translation
from app.config import CHANNEL_USERNAME


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with Session() as session:
        stmt = select(User).filter_by(id=update.effective_user.id)
        result = session.execute(stmt)
        user: Optional[User] = result.scalar_one_or_none()
        context.user_data['language'] = user.preferred_language if user else 'ru'

        if user:
            if await check_subscription_status(update, context):
                await update.message.reply_text(get_translation(context.user_data, 'welcome'))
            else:
                await update.message.reply_text(
                    get_translation(context.user_data, 'join_channel').format(channel=CHANNEL_USERNAME))
        else:
            await update.message.reply_text(get_translation(context.user_data, 'subscribe'))
            new_user = User(id=update.effective_user.id, username=update.effective_user.username, preferred_language='ru')
            new_chat = Chat(user_id=update.effective_user.id, inquire_history=jsonpickle.dumps([]),
                            event_history=jsonpickle.dumps([]))
            session.add_all([new_user, new_chat])
            session.commit()
