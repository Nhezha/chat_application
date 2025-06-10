from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from models.base import db
import uuid
from datetime import datetime
from config import app
class User(db.Model):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(String(36), primary_key=True)
    email: Mapped[str]  = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # with app.app_context():
    #     db.create_all()