from sqlalchemy import ForeignKey, Column, String, Enum
from sqlalchemy.orm import relationship
from source.db import Base
import enum

class CardTypeEnum(enum.Enum):
    auv = "Auvergne"
    burg = "Burgundy"
    lyon = "Lyonnais"
    prov = "Provence"


class RarityEnum(enum.Enum):
    std = "standard"
    rare = "rare"
    lgnd = "legendary"



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
    set = relationship("Cards", back_populates="")

    def __repr__(self):
        return f'Card: {self.id}'
        # TODO to string function
