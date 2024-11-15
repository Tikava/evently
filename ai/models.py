import vertexai
from vertexai.generative_models import GenerativeModel

# from config import GEMINI_API_KEY
from ai.settings import base_model_description, inquier_model_description

# genai.configure(api_key=GEMINI_API_KEY)
PROJECT_ID = 'gen-lang-client-0534670514'
REGION = 'us-central1'
vertexai.init(project=PROJECT_ID, location=REGION)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseModel(metaclass=SingletonMeta):
    def __init__(self) -> None:
        if not hasattr(self, 'model'):  # Prevent reinitialization
            self.model = GenerativeModel(**base_model_description)

    def get_model(self) -> GenerativeModel:
        return self.model


class InquireModel(metaclass=SingletonMeta):
    def __init__(self) -> None:
        if not hasattr(self, 'model'):  # Prevent reinitialization
            self.model = GenerativeModel(**inquier_model_description)

    def get_model(self) -> GenerativeModel:
        return self.model
