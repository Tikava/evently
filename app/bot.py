from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
)

from app.config import BOT_TOKEN

# Handlers
from handlers.start import start
from handlers.language import (
    select_language,
    language_callback
)
from handlers.conversation.conversation import conv_handler
from handlers.conversation.callbacks import (
    try_again_callback,
    save_callback,
    related_places_callback
)
from handlers.profile import (
    profile,
    my_events_callback,
    previous_event_view,
    next_event_view,
    current_event_view,
    remove_current_event_from_favs
)
from handlers.subscription import subscribe


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    # Profile
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CallbackQueryHandler(profile, pattern='^profile$'))
    app.add_handler(CallbackQueryHandler(my_events_callback, pattern='^my_events$'))
    app.add_handler(CallbackQueryHandler(current_event_view, pattern='^current_event_view$'))
    app.add_handler(CallbackQueryHandler(previous_event_view, pattern='^previous_event_view$'))
    app.add_handler(CallbackQueryHandler(next_event_view, pattern='^next_event_view$'))
    app.add_handler(CallbackQueryHandler(remove_current_event_from_favs, pattern='^remove_event$'))

    # Subscription
    app.add_handler(CommandHandler("subscribe", subscribe))
    
    # Language
    # app.add_handler(CommandHandler("language", select_language))
    app.add_handler(CallbackQueryHandler(select_language, pattern='^language$'))
    app.add_handler(CallbackQueryHandler(language_callback, pattern='^(en|ru)$'))
    # app.add_handler(CallbackQueryHandler(language_callback, )
    
    # Conversation
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(try_again_callback, pattern='^try_again$'))
    app.add_handler(CallbackQueryHandler(save_callback, pattern='^save$'))
    app.add_handler(CallbackQueryHandler(related_places_callback, pattern='^related_places$'))
    
    app.run_polling()