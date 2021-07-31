from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from source.db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)
    days_since_lgnd = Column(Integer)
    pull_available = Column(Boolean)
    deck_private = Column(Boolean)

    card_instances = relationship("CardInstance", back_populates="user")
