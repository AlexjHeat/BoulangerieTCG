from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from source.db import Base
from source.models.card_instance import CardInstance

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)
    days_since_legend = Column(Integer)
    pull_available = Column(Boolean)
    deck_private = Column(Boolean)

    card_instances = relationship("CardInstance", back_populates="user")


    def add_to_collection(self, session, card_id, n=1):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            session.add(CardInstance(user_id=self.id, card_id=card_id, level=1, quantity=0, active=False))
        else:
            q.quantity += n


    def remove_from_collection(self, session, card_id, n):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return False
        else:
            q.quantity -= n
        if q.quantity < 0:
            q.quantity = 0

    def check_collection(self, session, card_id, n):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return False
        if q.quantity < n:
            return False
        return True

