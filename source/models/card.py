from sqlalchemy import ForeignKey, Column, String, Enum
from sqlalchemy.orm import relationship
from source.db import Base

import enum

class HouseEnum(enum.Enum):
    auvergne = "AUV"
    burgundy = "BUR"
    lyonnais = "LYO"
    provence = "PRO"


class RarityEnum(enum.Enum):
    standard = "STD"
    rare = "RAR"
    legendary = "LGN"



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

    def __repr__(self):
        return f'Card: {self.id}'
        # TODO to string function
