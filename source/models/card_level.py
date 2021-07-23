from sqlalchemy import Column, Integer, String
from source.db import Base

class CardLevel(Base):
    __table__ = 'card Levels'
    post = Column(Integer)
    lurk = Column(Integer)
    react = Column(Integer)
    artPath = Column(String)