from sqlalchemy import Column, Integer, String

from backend.psql import Base, DBSession, engine

session = DBSession()


# The followings are the sqlalchemy model


class Model(Base):
    __tablename__ = 'model'
    django_orm_id = Column(Integer, unique=True, primary_key=True)
    bigg_id = Column(String(127), unique=True, index=True)


class Reaction(Base):
    __tablename__ = 'reaction'
    django_orm_id = Column(Integer, unique=True, primary_key=True)
    bigg_id = Column(String(127), unique=True, index=True)
    name = Column(String(255))


class Metabolite(Base):
    __tablename__ = 'metabolite'
    django_orm_id = Column(Integer, unique=True, primary_key=True)
    bigg_id = Column(String(127), unique=True, index=True)
    name = Column(String(511))


class Gene(Base):
    __tablename__ = 'gene'
    django_orm_id = Column(Integer, unique=True, primary_key=True)
    bigg_id = Column(String(127), unique=True, index=True)
    name = Column(String(127))


# Create the models above this line
Base.metadata.create_all(engine)
