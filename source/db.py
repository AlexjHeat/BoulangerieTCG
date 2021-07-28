from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from source.config import DATABASE_URI


engine = create_engine(DATABASE_URI)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine, autocommit=False))
