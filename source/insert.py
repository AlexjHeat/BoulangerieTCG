from source.models.card import Card
from source.db import Base, Session, engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)





