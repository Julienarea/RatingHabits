from sqlalchemy import create_engine, func, select, update, delete
from sqlalchemy.orm import sessionmaker, Session
from .models import *
from auth import hash_password, verify_password

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

    # ==================== USER METHODS ====================
    
    def add_user(self, nickname: str, username: str, email: str, password: str) -> User:
        """
        Добавить нового пользователя в базу данных.
        
        Args:
            nickname: Отображаемое имя пользователя
            username: Уникальное имя для входа
            email: Email пользователя
            password: Пароль в открытом виде (будет хеширован)
            
        Returns:
            User: Созданный объект пользователя
        """
        session = self.get_session()
        try:
            hashed_password = hash_password(password)
            new_user = User(
                nickname=nickname,
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            # Сохраняем ID перед закрытием сессии
            user_id = new_user.id
            
            # Создаём статистику для пользователя
            user_stats = UserStats(user_id=user_id)
            session.add(user_stats)
            session.commit()
            
            # Получаем пользователя заново из базы, чтобы вернуть свежий объект
            session.expunge_all()
            return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.expunge(user)  # Отвязываем объект от сессии
            return user
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> User:
        """Получить пользователя по username"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user:
                session.expunge(user)  # Отвязываем объект от сессии
            return user
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> User:
        """Получить пользователя по email"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if user:
                session.expunge(user)  # Отвязываем объект от сессии
            return user
        finally:
            session.close()

    def verify_user_password(self, user: User, password: str) -> bool:
        """
        Проверить пароль пользователя.
        
        Args:
            user: Объект пользователя
            password: Пароль для проверки
            
        Returns:
            bool: True если пароль верный
        """
        return verify_password(password, user.hashed_password)

    # ==================== STATS METHODS ====================
    
    def get_user_stats(self, user_id: int) -> UserStats:
        """Получить статистику пользователя"""
        session = self.get_session()
        try:
            stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
            if stats:
                session.expunge(stats)
            return stats
        finally:
            session.close()

    def update_user_rating(self, user_id: int, value: int):
        """Обновить рейтинг пользователя"""
        session = self.get_session()
        try:
            stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
            if stats:
                stats.rating = value
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_user_rating(self, user_id: int, value: int):
        """Добавить к рейтингу пользователя"""
        session = self.get_session()
        try:
            stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
            if stats:
                stats.rating += value
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== TASK METHODS ====================
    
    def add_user_task(self, user_id: int, title: str, notes: str = None, difficulty: str = 'easy', deadline=None) -> Task:
        """
        Добавить задачу пользователю.
        
        Args:
            user_id: ID пользователя
            title: Название задачи
            notes: Заметки к задаче (опционально)
            difficulty: Сложность задачи (trivial, easy, medium, hard)
            deadline: Крайний срок (опционально)
            
        Returns:
            Task: Созданная задача
        """
        session = self.get_session()
        try:
            new_task = Task(
                user_id=user_id,
                title=title,
                notes=notes,
                difficulty=difficulty,
                deadline=deadline
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)
            task_id = new_task.id
            session.expunge(new_task)
            return new_task
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_tasks(self, user_id: int, status: str = None):
        """
        Получить задачи пользователя.
        
        Args:
            user_id: ID пользователя
            status: Фильтр по статусу (опционально)
            
        Returns:
            List[Task]: Список задач
        """
        session = self.get_session()
        try:
            query = session.query(Task).filter(Task.user_id == user_id)
            if status:
                query = query.filter(Task.status == status)
            tasks = query.all()
            for task in tasks:
                session.expunge(task)
            return tasks
        finally:
            session.close()

    def update_task_status(self, task_id: int, status: str):
        """Обновить статус задачи"""
        session = self.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                if status == 'completed':
                    task.completed_at = func.now()
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_task_details(self, task_id: int, title: str, notes: str = None, difficulty: str = 'easy', deadline=None):
        """Обновить полную информацию о задаче"""
        session = self.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.title = title
                task.notes = notes
                task.difficulty = difficulty
                if deadline:
                    from datetime import datetime
                    task.deadline = datetime.fromisoformat(deadline)
                else:
                    task.deadline = None
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_task(self, task_id: int):
        """Удалить задачу"""
        session = self.get_session()
        try:
            session.query(Task).filter(Task.id == task_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== HABIT METHODS ====================
    
    def add_user_habit(self, user_id: int, title: str, notes: str = None) -> Habit:
        """
        Добавить привычку пользователю.
        
        Args:
            user_id: ID пользователя
            title: Название привычки
            notes: Заметки к привычке (опционально)
            
        Returns:
            Habit: Созданная привычка
        """
        session = self.get_session()
        try:
            new_habit = Habit(
                user_id=user_id,
                title=title,
                notes=notes,
                streak=0
            )
            session.add(new_habit)
            session.commit()
            session.refresh(new_habit)
            habit_id = new_habit.id
            session.expunge(new_habit)
            return new_habit
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_habits(self, user_id: int):
        """Получить привычки пользователя"""
        session = self.get_session()
        try:
            habits = session.query(Habit).filter(Habit.user_id == user_id).all()
            for habit in habits:
                session.expunge(habit)
            return habits
        finally:
            session.close()

    def update_habit_streak(self, habit_id: int, streak: int):
        """Обновить серию привычки"""
        session = self.get_session()
        try:
            habit = session.query(Habit).filter(Habit.id == habit_id).first()
            if habit:
                habit.streak = streak
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_habit(self, habit_id: int):
        """Удалить привычку"""
        session = self.get_session()
        try:
            session.query(Habit).filter(Habit.id == habit_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== ACHIEVEMENT METHODS ====================
    
    def add_user_achievement(self, user_id: int, title: str, description: str = None) -> Achievement:
        """
        Добавить достижение пользователю.
        
        Args:
            user_id: ID пользователя
            title: Название достижения
            description: Описание достижения
            
        Returns:
            Achievement: Созданное достижение
        """
        session = self.get_session()
        try:
            new_achievement = Achievement(
                user_id=user_id,
                title=title,
                description=description
            )
            session.add(new_achievement)
            session.commit()
            session.refresh(new_achievement)
            achievement_id = new_achievement.id
            session.expunge(new_achievement)
            return new_achievement
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_achievements(self, user_id: int):
        """Получить достижения пользователя"""
        session = self.get_session()
        try:
            achievements = session.query(Achievement).filter(Achievement.user_id == user_id).all()
            for ach in achievements:
                session.expunge(ach)
            return achievements
        finally:
            session.close()


# Глобальный экземпляр для использования в приложении
db = Database()
SessionLocal = db.SessionLocal