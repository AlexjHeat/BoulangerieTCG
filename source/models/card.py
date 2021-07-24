from sqlalchemy import ForeignKey, Column, String, Integer, Enum
from sqlalchemy.orm import relationship
from source.db import Base
from source.models import card_instance, card_level, set
import enum

class CardTypeEnum(enum.Enum):
    auv = "AUVERGNE"
    burg = "BURGUNDY"
    lyon = "LYONNAIS"
    prov = "PROVENCE"


class RarityEnum(enum.Enum):
    std = "STANDARD"
    rare = "RARE"
    lgnd = "LEGENDARY"



class Card(Base):
    __tablename__ = 'cards'
    id = Column(String, primary_key=True)
    prefix = Column(String, ForeignKey('sets.prefix'))
    title = Column(String)
    type = Column(Enum(CardTypeEnum))
    rarity = Column(Enum(RarityEnum))
    artPath = Column(String)

    card_instances = relationship("CardInstance", back_populates="card")
    card_levels = relationship("CardLevel", back_populates="card")
    set = relationship("Set", back_populates="cards")

    def __repr__(self):
        return f'Card: {self.id}'
        # TODO to string function
