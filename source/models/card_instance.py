from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from source.db import Base


class CardInstance(Base):
    __tablename__ = 'card_instances'
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    card_id = Column(String, ForeignKey('cards.id', ondelete="CASCADE"), primary_key=True)
    quantity = Column(Integer)
    level = Column(Integer)
    active = Column(Boolean)

    user = relationship("User", back_populates="card_instances")
    card = relationship("Card", back_populates="card_instances")

    def __init__(self, user_id, card_id, quantity, level, active):
        self.user_id = user_id
        self.card_id = card_id
        self.quantity = quantity
        self.level = level
        self.active = active
