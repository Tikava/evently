from typing import Optional

from sqlalchemy.future import select

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.translation import get_translation
from database.db import Session
from models.base import Event


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [[InlineKeyboardButton(get_translation(context.user_data, 'my_events'), callback_data="my_events"),
                 InlineKeyboardButton(get_translation(context.user_data, 'language'), callback_data="language")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    main_menu_id = context.user_data.get('main_menu', None)
    if main_menu_id:
        await context.bot.edit_message_text(chat_id=user.id, message_id=main_menu_id,
                                            text=f"{get_translation(context.user_data, 'your_profile')} <b>{user.first_name}</b>!",
                                            parse_mode="HTML", reply_markup=reply_markup)
    else:
        message = await context.bot.send_message(chat_id=user.id,
                                                 text=f"{get_translation(context.user_data, 'your_profile')} <b>{user.first_name}</b>!",
                                                 parse_mode="HTML", reply_markup=reply_markup)
        context.user_data['main_menu'] = message.id


async def my_events_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user

    with Session() as session:
        stmt = select(Event).filter_by(user_id=user.id)
        result = session.execute(stmt)
        user_events = result.scalars().all()

        # Events not found
        if len(user_events) == 0:
            await update.callback_query.answer(get_translation(context.user_data, 'no_events'), show_alert=True)
            return

        context.user_data['user_events'] = user_events

        sub_keyboard = []

        current_index_front = 0

        if 'index' not in context.user_data:
            context.user_data['index'] = {
                'current': {'front': 0, 'back': user_events[0].id},
                'next': {'front': 0, 'back': 0},
                'previous': {'front': 0, 'back': 0}
            }

        context.user_data['index']['current']['front'] = current_index_front
        context.user_data['index']['current']['back'] = user_events[current_index_front].id

        sub_keyboard.append(InlineKeyboardButton(f"• {current_index_front+1} •", callback_data="current_event_view"))

        if current_index_front != 0:
            previous_index_front = current_index_front - 1
            context.user_data['index']['previous']['front'] = previous_index_front
            context.user_data['index']['previous']['back'] = user_events[previous_index_front].id
            sub_keyboard.insert(0, InlineKeyboardButton(f"⮜ {previous_index_front+1}", callback_data="previous_event_view"))

        if len(user_events) > 1:
            next_index_front = current_index_front + 1
            context.user_data['index']['next']['front'] = next_index_front
            context.user_data['index']['next']['back'] = user_events[next_index_front].id
            sub_keyboard.append(InlineKeyboardButton(f"{next_index_front+1} ⮞", callback_data="next_event_view"))


        current_event = user_events[current_index_front]

        keyboard = [sub_keyboard,
                    [InlineKeyboardButton(get_translation(context.user_data, 'remove_event'), callback_data='remove_event')],
                    [InlineKeyboardButton(get_translation(context.user_data, 'back'), callback_data="profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_text(current_event.text, chat_id=user.id,
                                            message_id=context.user_data['main_menu'], reply_markup=reply_markup, parse_mode="HTML")


async def remove_current_event_from_favs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_index_back = context.user_data['index']['current']['back']
    # user = update.effective_user
    # event = context.user_data['user_events'][current_event_index]

    with Session() as session:
        stmt = select(Event).filter_by(id=current_index_back)
        result = session.execute(stmt)
        event = result.scalars().first()
        session.delete(event)
        session.commit()

    await my_events_callback(update, context)


async def current_event_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer(get_translation(context.user_data, 'current_event'))


async def next_event_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    previous_index_front = context.user_data['index']['current']['front']
    current_index_front = context.user_data['index']['next']['front']

    context.user_data['index']['previous']['front'] = previous_index_front
    context.user_data['index']['previous']['back'] = context.user_data['index']['current']['back']

    context.user_data['index']['current']['front'] = current_index_front
    context.user_data['index']['current']['back'] = context.user_data['index']['next']['back']

    sub_keyboard = [
        InlineKeyboardButton(f"⮜ {previous_index_front+1}", callback_data="previous_event_view"),
        InlineKeyboardButton(f"• {current_index_front+1} •", callback_data="current_event_view")
    ]

    if current_index_front < (len(context.user_data['user_events']) - 1):
        next_index_front = current_index_front + 1
        context.user_data['index']['next']['front'] = next_index_front
        context.user_data['index']['next']['back'] = context.user_data['user_events'][next_index_front].id
        sub_keyboard.append(InlineKeyboardButton(f"{next_index_front+1} ⮞", callback_data="next_event_view"))


    current_event = context.user_data['user_events'][current_index_front]

    keyboard = [sub_keyboard,
                [InlineKeyboardButton(get_translation(context.user_data, 'remove_event'), callback_data='remove_event')],
                [InlineKeyboardButton(get_translation(context.user_data, 'back'), callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(current_event.text, chat_id=update.effective_user.id,
                                        message_id=context.user_data['main_menu'], reply_markup=reply_markup, parse_mode="HTML")


async def previous_event_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_index_front = context.user_data['index']['previous']['front']
    next_index_front = context.user_data['index']['current']['front']

    context.user_data['index']['current']['front'] = current_index_front
    context.user_data['index']['current']['back'] = context.user_data['index']['previous']['back']

    context.user_data['index']['next']['front'] = next_index_front
    context.user_data['index']['next']['back'] = context.user_data['index']['current']['back']

    sub_keyboard = [
        InlineKeyboardButton(f"• {current_index_front+1} •", callback_data="current_event_view"),
        InlineKeyboardButton(f"{next_index_front+1} ⮞", callback_data="next_event_view")
    ]

    if current_index_front != 0:
        previous_index_front = current_index_front - 1
        context.user_data['index']['previous']['front'] = previous_index_front
        context.user_data['index']['previous']['back'] = context.user_data['user_events'][previous_index_front].id
        sub_keyboard.insert(0, InlineKeyboardButton(f"⮜ {previous_index_front+1}", callback_data="previous_event_view"))

    current_event = context.user_data['user_events'][current_index_front]

    keyboard = [sub_keyboard,
                [InlineKeyboardButton(get_translation(context.user_data, 'remove_event'), callback_data='remove_event')],
                [InlineKeyboardButton(get_translation(context.user_data, 'back'), callback_data="profile")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_text(current_event.text, chat_id=update.effective_user.id,
                                        message_id=context.user_data['main_menu'], reply_markup=reply_markup, parse_mode="HTML")
