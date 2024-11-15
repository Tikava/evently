import json

import jsonpickle
from vertexai.generative_models import GenerativeModel, ChatSession

from ai.models import BaseModel, InquireModel
from database.db import Session
from models.base import Chat

base_model = BaseModel().get_model()
inquirer_model = InquireModel().get_model()


# Sending message to the model and retrieving the response
def send_message(model: GenerativeModel, user_id: int, user_input: str) -> dict:
    try:
        with Session() as session:
            chat = session.query(Chat).filter_by(user_id=user_id).one()

            # Decoding the history and restoring the chat session based on the model
            if model == base_model:
                history = jsonpickle.decode(chat.event_history)
                if history == "[]":
                    chat_session = base_model.start_chat(history=[])
                else:
                    chat_session = ChatSession(model=model, history=history)
            else:
                history = jsonpickle.decode(chat.inquire_history)
                if history == "[]":
                    chat_session = inquirer_model.start_chat(history=[])
                else:
                    chat_session = ChatSession(model=model, history=history)

            response = chat_session.send_message(user_input)

            # Encoding the history object, making it string and saving it to the database
            if model == base_model:
                chat.event_history = jsonpickle.encode(chat_session.history)
            else:
                chat.inquire_history = jsonpickle.encode(chat_session.history)
            session.commit()

            # Returning formatted response
            if model == base_model:
                return response.text
            return json.loads(response.text.replace("```", "").replace("json", "").strip())
    except Exception:
        raise Exception("No chat session found. Please start a new chat session.")
