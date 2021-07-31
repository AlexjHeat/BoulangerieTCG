from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from source.db import Base

class CardLevel(Base):
    __tablename__ = 'card_levels'
    card_id = Column(String, ForeignKey('cards.id', ondelete="CASCADE"), primary_key=True)
    level = Column(Integer, primary_key=True)
    post = Column(Integer)
    lurk = Column(Integer)
    react = Column(Integer)
    artPath = Column(String)

    card = relationship("Card", back_populates="card_levels")
