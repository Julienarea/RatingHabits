from sqlalchemy import create_engine, func, select, update, delete
from sqlalchemy.orm import sessionmaker, Session
from .models import *

from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DB_URL")

class Database:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def add_user(self, nickname, username, email, hashed_password):
        continue

    def add_user_rating(user_id, value):
        continue

    def add_user_task(user_id, Task):
        continue

    def add_user_habits(user_id, Habit):
        continue