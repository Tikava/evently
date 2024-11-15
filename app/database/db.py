from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


class DatabaseManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._engine = None
            cls._instance._Session = None
        return cls._instance
    
    def __init__(self, db_url='sqlite:///storage.db'):
        if self._engine is None:
            self._engine = create_engine(db_url, echo=True)
            Base.metadata.create_all(self._engine)
            self._Session = sessionmaker(bind=self._engine)

    def get_session(self):
        return self._Session

    
db_manager = DatabaseManager()
Session = db_manager.get_session()
