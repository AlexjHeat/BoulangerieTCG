from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import config


engine = create_engine(config.DATABASE_URI, echo=True)
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=engine))
