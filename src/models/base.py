
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os


DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')

engine = create_engine(DATABASE_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

def init_db():
    """Initialize the database, creating tables if they don't exist."""
    Base.metadata.create_all(engine)