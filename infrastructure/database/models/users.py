from typing import Optional, List
from datetime import datetime

from sqlalchemy import String, func, TIMESTAMP, INTEGER
from sqlalchemy import text, BIGINT, Boolean, true, ForeignKey, false
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    language_code: Mapped[str] = mapped_column(String(10), server_default=text("'ru'"))

    profile: Mapped["Profile"] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User {self.user_id} {self.username} {self.full_name}>"

    __tablename__ = "user"


class Profile(Base):
    banned: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String, default="ru")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_active: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    gender: Mapped[Boolean] = mapped_column(Boolean, nullable=True)     # 0 - female, 1 - male
    age: Mapped[int] = mapped_column(INTEGER, nullable=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=True)
    captcha: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), primary_key=True, autoincrement=False)
    user: Mapped["User"] = relationship(back_populates="profile")

    def __repr__(self):
        return f"<Profile of User {self.user_id} {self.user.username} {self.user.full_name}>"

    __tablename__ = "profile"
