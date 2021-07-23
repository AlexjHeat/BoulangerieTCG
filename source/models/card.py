from sqlalchemy import Column, String, Enum
from source.db import Base
import enum

class cardTypeEnum(enum.Enum):
    auv = "Auvergne"
    burg = "Burgundy"
    lyon = "Lyonnais"
    prov = "Provence"



class Card(Base):
    __tablename__ = 'cards'
    id = Column('Card ID', String, primary_key=True)
    title = Column(String)
    type = Column('value', Enum(cardTypeEnum))
    artPath = Column(String)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f'Card: {self.id}'
        # TODO to string function
