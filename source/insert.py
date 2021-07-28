from source.models.card import Card
from source.models.user import User
from source.models.card_instance import CardInstance
from source.models.card_level import CardLevel
from source.models.set import Set
from source.db import Base, Session, engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = Session()

session.add(Set(prefix="LB", name="La Boulangerie", total_cards=4))

session.add(Card(id="LB1", prefix="LB", title="Kitch's revenge", house="BURG", rarity="RARE"))
session.add(Card(id="LB2", prefix="LB", title="shiba", house="PROV", rarity="STD"))
session.add(Card(id="LB3", prefix="LB", title="toortle", house="LYON", rarity="RARE"))
session.add(Card(id="LB4", prefix="LB", title="pepsi", house="AUV", rarity="LGN"))

session.commit()
session.close()