import re

from telegram import Update, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from utils.translation import get_translation
from utils.helpers import subscription_required

from ai.generation import send_message
from ai.models import BaseModel, InquireModel

BASE_MODEL = BaseModel().get_model()
INQUIRER_MODEL = InquireModel().get_model()

HANDLE_USER_OUTPUT, BACK_CLICKED = range(2)


@subscription_required
async def use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = send_message(INQUIRER_MODEL, update.effective_user.id,
                            get_translation(context.user_data, 'to_bot_conversation_started'))
    context.user_data["response"] = response
    context.user_data["flag"] = False
    context.user_data["answers"] = []

    reply_markup = None
    if len(response["possible_answers"]) > 0:
        keyboard = [[KeyboardButton(response["possible_answers"][i])] for i in range(len(response["possible_answers"]))]
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    # Sending the first question to the user and waiting for the answer
    await context.bot.send_message(update.effective_chat.id, response["question"], reply_markup=reply_markup)
    return HANDLE_USER_OUTPUT


async def handle_user_output(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answer = update.message.text
    if user_answer == get_translation(context.user_data, 'back'):
        await handle_click_back(update, context)
        return HANDLE_USER_OUTPUT
    else:
        flag = context.user_data["flag"]
        if flag:
            context.user_data["answers"][-1] = dict(question=context.user_data["response"]["question"],
                                                    answer=user_answer)
            context.user_data["flag"] = False
        else:
            context.user_data["answers"].append(
                dict(question=context.user_data["response"]["question"], answer=user_answer))

        response = send_message(INQUIRER_MODEL, update.effective_user.id, user_answer)
        context.user_data["response"] = response

        # reply_markup = None
        keyboard = None

        if len(response["possible_answers"]) > 0:
            keyboard = [[KeyboardButton(response["possible_answers"][i])] for i in
                        range(len(response["possible_answers"]))]

        if keyboard is None:
            keyboard = [[KeyboardButton(get_translation(context.user_data, 'back'))]]
        else:
            keyboard.append([KeyboardButton(get_translation(context.user_data, 'back'))])
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

        continues = context.user_data['response']['continue_asking']

        if continues:
            await context.bot.send_message(update.effective_chat.id, response["question"], reply_markup=reply_markup)
            return HANDLE_USER_OUTPUT
        else:
            await generate_event_plan_and_send(update, context)
            return ConversationHandler.END


async def handle_click_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # We got here previous question
    response = send_message(INQUIRER_MODEL, update.effective_user.id,
                            get_translation(context.user_data, 'to_bot_clicked_back'))
    context.user_data["response"] = response
    context.user_data["flag"] = True
    if len(response["possible_answers"]) > 0:
        keyboard = [[KeyboardButton(response["possible_answers"][i])] for i in range(len(response["possible_answers"]))]
        reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        await context.bot.send_message(update.effective_chat.id, response["question"], reply_markup=reply_markup)
    else:
        await context.bot.send_message(update.effective_chat.id, response["question"],
                                       reply_markup=ReplyKeyboardRemove())

    return HANDLE_USER_OUTPUT


# Sending event plan to user
async def generate_event_plan_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_translation(context.user_data, 'questions_answered'),
                                    reply_markup=ReplyKeyboardRemove())
    message = await context.bot.send_message(update.effective_chat.id,
                                             get_translation(context.user_data, 'generating_event_plan'))

    try:
        requirements = context.user_data.get("answers", [])
        print(requirements)
        event_plan = send_message(BASE_MODEL, update.effective_user.id, str(requirements))
        #Setting up the inline keyboard
        keyboard = [[InlineKeyboardButton(get_translation(context.user_data, 'save'), callback_data="save"),
                     InlineKeyboardButton(get_translation(context.user_data, 'related_places'),
                                          callback_data="related_places"),
                     InlineKeyboardButton(get_translation(context.user_data, 'generate_again'),
                                          callback_data="try_again")],
                    [InlineKeyboardButton(get_translation(context.user_data, 'my_profile'), callback_data="profile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # context.user_data['event_keywords'] = event_plan_json['event_keywords']

        # Formatting the event plan
        pattern = r"\*\*(.*?)\*\*"
        replacement = r"<b>\1</b>"
        # plan = f"""**{get_translation(context.user_data, 'event_name')}**: {event_plan_json['event_name']}\n\n**{get_translation(context.user_data, 'event_overview')}**: {event_plan_json['event_overview']}\n\n**{get_translation(context.user_data, 'event_plan')}**: {event_plan_json['detailed_event_plan']}\n\n"""
        formatted_plan = re.sub(pattern, replacement, event_plan).replace("* ", '• ')

        await context.bot.edit_message_text(text=formatted_plan, chat_id=update.effective_chat.id,
                                            message_id=message.id, parse_mode='HTML', reply_markup=reply_markup)
        context.user_data['event_plan'] = message.id
        context.user_data['main_menu'] = None
    except Exception as e:
        print("An error occurred while generating the event plan:", e)

        # Deleting the "Generating plan msg"
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.id)

        # Sending the error message
        keyboard = [[InlineKeyboardButton("😅 Try again", callback_data="try_again")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await context.bot.send_message(update.effective_chat.id,
                                                 get_translation(context.user_data, 'error_generating_plan'),
                                                 reply_markup=reply_markup)
        context.user_data['error_message'] = message.id


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(get_translation(context.user_data, 'conversation_ended'),
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("use", use)],
    states={
        HANDLE_USER_OUTPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_output)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, fallback),
    ],
)
