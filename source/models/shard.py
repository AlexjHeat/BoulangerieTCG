from sqlalchemy import Column, Integer, Boolean
from source.db import Base

class Shard(Base):
    __tablename__ = 'shards'
    quantity = Column(Integer)
    level = Column(Integer)
    active = Column(Boolean)