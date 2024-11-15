import json
import jsonpickle
from vertexai.generative_models import GenerativeModel, ChatSession
from app.ai.models import BaseModel, InquireModel
from app.database.db import Session
from app.database.models import Chat
inquirer_model = InquireModel().get_model()
base_model = BaseModel().get_model()


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
                return json.loads(response.text.replace("```", "").replace("json", "").strip())
            response_text = response.text.replace("```", "")
            response_text = response_text.replace("json", "")
            response_text = response_text.strip()
            return json.loads(response_text)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception("No chat session found. Please start a new chat session.") from e
