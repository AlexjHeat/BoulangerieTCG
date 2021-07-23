from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from source.db import Base

class CardInstance(Base):
    __tablename__ = 'card_instances'
    user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    card_id = Column(String, ForeignKey('cards.id'), primary_key=True)
    fragments = Column(Integer)
    level = Column(Integer)
    active = Column(Boolean)

    user = relationship("User", back_populates="card_instances")
    card = relationship("Card", back_populates="card_instances")
