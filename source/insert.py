from source.models.card import Card
from source.models.user import User
from source.models.card_instance import CardInstance
from source.models.card_level import CardLevel
from source.db import Base, Session, engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)





