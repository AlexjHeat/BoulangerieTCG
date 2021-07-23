from sqlalchemy import Column, String, Integer, Boolean
from source.db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column('User ID', String, primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)
    pull_available = Column(Boolean)
    deck_private = Column(Boolean)