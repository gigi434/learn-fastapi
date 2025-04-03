import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# Determine the absolute path to the database file based on the location of this file
BASE_DIR = Path(__file__).resolve().parent
SQLALCHEMY_DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "todosapp.db")}'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
