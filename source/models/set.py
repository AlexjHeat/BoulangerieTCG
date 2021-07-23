from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from source.db import Base

class Set(Base):
    __tablename__ = 'sets'
    prefix = Column(String, primary_key=True)
    name = Column(String)
    total_cards = Column(Integer)

    cards = relationship("Card", back_populates="set")