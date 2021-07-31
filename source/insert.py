from source.models.card import Card
from source.models.user import User
from source.models.card_instance import CardInstance
from source.models.card_level import CardLevel
from source.models.set import Set
from source.db import Base, Session, engine


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session = Session()

session.add(Set(prefix="LB", name="La Boulangerie", total_cards=4, boosted=False))

session.add(Card(id="LB1", prefix="LB", title="Kitch's revenge", house="burgundy", rarity="rare", flavor="You yanks 'ave it comin I swear on me mum I do"))
session.add(Card(id="LB2", prefix="LB", title="shiba", house="provence", rarity="legendary", flavor="half dog, half mascot"))
session.add(Card(id="LB3", prefix="LB", title="toortle", house="lyonnais", rarity="standard", flavor="ye"))

test = Card(id="LB4", prefix="LB", title="pepsi", house="auvergne", rarity="legendary", flavor="drink piss")
test.flavor = 'no really, drink piss'
session.add(test)

session.commit()
session.close()
