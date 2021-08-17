from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from source.db import Base
from .card_instance import CardInstance
from .card_level import CardLevel
from .card import Card

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
        if n < 0:
            return
        q = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                               CardInstance.card_id == card_id).one_or_none()
        if q is None:
            q = CardInstance(user_id=self.id, card_id=card_id, level=0, quantity=n, active=False)
            session.add(q)
        else:
            q.quantity += n

        if q.level == 0:
            q.level += 1
            q.quantity -= 1

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

    def clear_active(self, session):
        active_list = session.query(CardInstance).filter(CardInstance.user_id == self.id, CardInstance.active).all()
        for card in active_list:
            card.active = False

    def set_active(self, session, card_id):
        card = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                                  CardInstance.card_id == card_id).one_or_none()
        if card is None:
            return False
        if card.level <= 0:
            return False

        card.active = True

    def get_active(self, session):
        active_list = session.query(CardInstance).filter(CardInstance.user_id == self.id, CardInstance.active).all()
        level_list = []
        for card in active_list:
            level_list.append(session.query(CardLevel).filter(CardLevel.card_id == card.card_id,
                                                              CardLevel.level == card.level).one())
        return level_list

    def get_upgrade_info(self, session, card_id):
        instance = session.query(CardInstance).filter(CardInstance.user_id == self.id,
                                                      CardInstance.card_id == card_id).one()
        next_level = instance.level + 1
        amount_needed = max(0, next_level - instance.quantity)
        return next_level, amount_needed
