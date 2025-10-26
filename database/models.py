from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    func,
    Text,
    Index,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, relationship
from flask_login import UserMixin

Base = declarative_base()

class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    path_to_avatar = Column(String, default='default_avatar.png')
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", uselist=False, back_populates="user", cascade="all, delete-orphan")

class UserStats(Base):
    __tablename__ = 'user_stats'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    rating = Column(Integer, default=1000)
    total_tasks_completed = Column(Integer, default=0)
    rating_change_for_the_week = Column(Integer, default=0)
    rating_change_for_the_day = Column(Integer, default=0)
    user = relationship("User", back_populates="stats")

class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    difficulty = Column(String, default='easy')
    streak = Column(Integer, default=0)
    start_date = Column(String, nullable=True)  # Дата начала (строка формата YYYY-MM-DD)
    repeat_type = Column(String, default='weekly')  # daily, weekly, monthly, yearly
    repeat_every = Column(Integer, default=1)  # Повторять каждые N периодов
    repeat_days = Column(String, default='1,2,3,4,5')  # Дни недели (строка вида '0,1,2,3,4,5,6')
    user = relationship("User", back_populates="habits")


class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    achieved_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="achievements")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String, default='in_progress')  # in_progress, completed
    difficulty = Column(String, default='easy')  # trivial, easy, medium, hard
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    user = relationship("User", back_populates="tasks")

