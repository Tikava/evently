from typing import List

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_table"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    
    events: Mapped[List["Event"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")
    chat: Mapped["Chat"] = relationship(back_populates="user")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Event(Base):
    __tablename__ = "event_table"


    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text())
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))

    user: Mapped["User"] = relationship(back_populates="events")


class Chat(Base):
    __tablename__ = "chat_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    inquire_history: Mapped[str] = mapped_column(Text())
    event_history: Mapped[str] = mapped_column(Text())
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    
    user: Mapped["User"] = relationship(back_populates="chat")