from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv
load_dotenv()

# Замените строку подключения на свою (пример для PostgreSQL)
DATABASE_URL = os.getenv('DB_URL')

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Synced")
