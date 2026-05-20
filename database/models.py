from datetime import datetime, date
from sqlalchemy import BigInteger, ForeignKey, String, Integer, Boolean, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base

class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_failures: Mapped[int] = mapped_column(Integer, default=0)
    total_clean_days: Mapped[int] = mapped_column(Integer, default=0)
    join_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    xp_points: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    freezes_available: Mapped[int] = mapped_column(Integer, default=1)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    daily_checks: Mapped[list["DailyCheck"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[list["Achievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    freeze_usages: Mapped[list["FreezeUsage"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class DailyCheck(Base):
    __tablename__ = 'daily_checks'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete="CASCADE"), nullable=False)
    check_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False) # 'clean', 'relapsed', 'freeze'
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="daily_checks")

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete="CASCADE"), nullable=False)
    badge_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="achievements")

class FreezeUsage(Base):
    __tablename__ = 'freeze_usages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete="CASCADE"), nullable=False)
    used_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="freeze_usages")

class Chat(Base):
    __tablename__ = 'chats'
    
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
