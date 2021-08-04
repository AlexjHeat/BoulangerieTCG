from sqlalchemy import ForeignKey, Column, String, Enum
from sqlalchemy.orm import relationship
from source.db import Base
from source.models.card_level import CardLevel

import enum

class HouseEnum(enum.Enum):
    auvergne = 1
    burgundy = 2
    lyonnais = 3
    provence = 4


class RarityEnum(enum.Enum):
    standard = 1
    rare = 2
    legendary = 3



class Card(Base):
    __tablename__ = 'cards'
    id = Column(String, primary_key=True)
    prefix = Column(String, ForeignKey('sets.prefix', ondelete="CASCADE"))
    title = Column(String)
    house = Column(Enum(HouseEnum))
    rarity = Column(Enum(RarityEnum))
    flavor = Column(String)
    artPath = Column(String)

    card_instances = relationship("CardInstance", back_populates="card")
    card_levels = relationship("CardLevel", back_populates="card")
    set = relationship("Set", back_populates="cards")

    def get_image_path(self, session, level):
        q = session.query(CardLevel).filter(CardLevel.card_id == self.id, CardLevel.level == level).one_or_none()
        if q is None:
            return False
        return q.artPath

