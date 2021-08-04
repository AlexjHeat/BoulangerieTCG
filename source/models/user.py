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

    def add_to_deck(self, session, card_id, n):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            session.add(CardInstance(user_id=self.id, card_id=card_id, level=0, quantity=n, active=False))
        else:
            q.quantity += n

    def remove_from_deck(self, session, card_id, n):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return False
        q.quantity -= n
        if q.quantity < 0:
            q.quantity = 0

    def get_quantity(self, session, card_id):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return 0
        return q.quantity

    def get_level(self, session, card_id):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return 0
        return q.level

    def set_level(self, session, card_id, lvl):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            q = CardInstance(user_id=self.id, card_id=card_id, quantity=0, level=lvl, active=False)
            session.add(q)
        else:
            q.level = lvl

    def fragments_from_destroy(self, session, card_id):
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            return 0
        if q.level == 0:
            return 0
        n = 1
        for x in range(q.level):
            n += x
        return n


