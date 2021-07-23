from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from source.db import Base
import enum

class cardTypeEnum(enum.Enum):
    auv = "Auvergne"
    burg = "Burgundy"
    lyon = "Lyonnais"
    prov = "Provence"



class Card(Base):
    __tablename__ = 'cards'
    id = Column(String, primary_key=True)
    title = Column(String)
    type = Column('value', Enum(cardTypeEnum))
    artPath = Column(String)

    card_instances = relationship("CardInstance", back_populates="card")
    card_levels = relationship("CardLevel", back_populates="card")

    def __repr__(self):
        return f'Card: {self.id}'
        # TODO to string function
