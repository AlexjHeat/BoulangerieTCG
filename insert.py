from source.models.card import Card
from source.models.set import Set
from source.models.card_instance import CardInstance
from source.models.card_level import CardLevel
from source.models.user import User
from source.db import Base, Session, engine

print('Program start...')
Base.metadata.drop_all(engine)
print('Tables dropped')
Base.metadata.create_all(engine)
print('Tables created')
session = Session()

session.add(Set(prefix="TST"))

session.commit()
print('Ending insertion session')
