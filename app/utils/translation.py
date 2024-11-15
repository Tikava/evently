LANGUAGES = {
    "en": "English",
    "ru": "Русский"
}

TRANSLATIONS = {
    'en': {
        'no_events': 'No events found.',
        'current_event': "It's current event.",
        'remove_event': '💔 Remove event',

        'generating_again_message': 'Generating event plan again...',
        'event_saved': 'Event saved successfully!',
        'no_places': 'No related places found.',
        
        'to_bot_conversation_started': '*conversation started*',
        'to_bot_clicked_back': '*User clicked back to change the answer for previous question*',
        'to_bot_generate_again': 'Generate event plan again differently from the previous one',
        
        'my_events': '✨ My Events',
        'language': '🌐 Language',
        'your_profile': 'This is your profile',
        'your_events': 'Here are your events',
        'language_selected': 'Language selected successfully!',
        'available_languages': 'Here are the available languages',
        'back': '⬅️ Back',
        'save': '⭐️ Save',
        'related_places': '📍 Related places',
        'generate_again': '🤨 Generate again',
        'my_profile': '👤 My Profile',
        'event_name': 'Event Name',
        'event_overview': 'Overview',
        'event_plan': 'Plan',   
        'welcome': "Welcome! You are subscribed. You can use the bot by typing /use.",
        'subscribe': "You are subscribed. You can use the bot by typing /use.",
        'join_channel': "Please join the channel @{channel} to access the bot's functionality.",
        'choose_language': "Please choose your language:",
        'what_to_plan': "What do you want to plan?",
        'error_generating': "Sorry, an error occurred while generating questions. Please try again later.",
        'conversation_ended': "An error occurred or you have used an invalid command. The conversation will end now.",
        'generating_event_plan': 'Generating your event plan...',
        'event_plan_ready': 'Your event plan is ready:',
        'error_generating_plan': 'An error occurred while generating your event plan.',
        'questions_answered': 'All questions have been answered.',
        'keyboard_input_missed': "Please try again and choose from the keyboard.",
        'asking_for_other': 'Write what you want...'
    },
    'ru': {
        'no_events': 'Мероприятия не найдены.',
        'current_event': 'Это текущее мероприятие.',
        'remove_event': '💔 Удалить мероприятие',

        'generating_again_message': 'Повторная генерация плана мероприятия...',
        'event_saved': 'Мероприятие успешно сохранено!',
        'no_places': 'Связанные места не найдены.',
        
        'to_bot_conversation_started': '*начало разговора*',
        'to_bot_clicked_back': '*Пользователь нажал назад, чтобы изменить ответ на предыдущий вопрос*',
        'to_bot_generate_again': 'Сгенерировать план мероприятия заново, отличным от предыдущего',
        
        'my_events': '✨ Мои Мероприятия',
        'language': '🌐 Язык',
        'your_profile': 'Это ваш профиль',
        'your_events': 'Вот ваши мероприятия',
        'language_selected': 'Язык успешно выбран!',
        'available_languages': 'Доступные языки',
        'back': '⬅️ Назад',
        'save': '⭐️ Сохранить',
        'related_places': '📍 Связанные места',
        'generate_again': '🤨 Сгенерировать снова',
        'my_profile': '👤 Мой Профиль',
        'event_name': 'Название мероприятия',
        'event_overview': 'Обзор',
        'event_plan': 'План',
        'welcome': "Добро пожаловать! Вы подписаны. Вы можете использовать бота, введя /use.",
        'subscribe': "Вы подписаны. Вы можете использовать бота, введя /use.",
        'join_channel': "Пожалуйста, присоединитесь к каналу @{channel}, чтобы использовать возможности бота.",
        'choose_language': "Пожалуйста, выберите ваш язык:",
        'what_to_plan': "Что вы хотите запланировать?",
        'error_generating': "Извините, при генерации вопросов произошла ошибка. Пожалуйста, попробуйте позже.",
        'conversation_ended': "Произошла ошибка или вы использовали недопустимую команду. Разговор сейчас закончится.",
        'generating_event_plan': "Генерация плана мероприятия...",
        'event_plan_ready': 'План мероприятий готов:',
        'error_generating_plan': "Извините, при генерации плана мероприятия произошла ошибка. Пожалуйста, попробуйте позже.",
        'questions_answered': 'Ответы на вопросы получены.',
        'keyboard_input_missed': "Пожалуйста, попробуйте снова и выберите из клавиатуры.",
        'asking_for_other': 'Напишите, что вы хотите...'
    }
}



def get_translation(user_data, key):
    language = user_data.get('language', 'en')
    return TRANSLATIONS[language][key]