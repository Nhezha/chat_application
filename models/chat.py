from sqlalchemy import Integer, String, Boolean, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import db
import uuid
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'

    chat_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    message_from: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email"), nullable=False
    )
    message_to: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    sender: Mapped["User"] = relationship(
        "User", backref="chats_sent", foreign_keys=[message_from]
    )
    receiver: Mapped["User"] = relationship(
        "User", backref="chats_received", foreign_keys=[message_to]
    )
