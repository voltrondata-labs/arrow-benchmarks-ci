from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from config import Config

Base = declarative_base()
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI, future=True, echo=False, pool_pre_ping=True
)
session_maker = sessionmaker(bind=engine)
Session = scoped_session(session_maker)
