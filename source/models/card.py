from sqlalchemy import ForeignKey, Column, String, Enum
from sqlalchemy.orm import relationship
from source.db import Base
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

    card_instances = relationship("CardInstance", back_populates="card", cascade="all, delete")
    card_levels = relationship("CardLevel", back_populates="card", cascade="all, delete")
    set = relationship("Set", back_populates="cards")

