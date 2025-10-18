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

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    stats = relationship("UserStats", uselist=False, back_populates="user", cascade="all, delete-orphan")

class Stats(Base):
    __tablename__ = 'stats'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    rating = Column(Integer, default=0)
    total_tasks_completed = Column(Integer, default=0)
    rating_change_for_the_week = Column(Integer, default=0)
    rating_change_for_the_day = Column(Integer, default=0)

class Habits(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    streak = Column(Integer, default=0)




    