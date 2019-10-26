from sqlalchemy import Column, String, func, or_, and_, desc, Integer
from backend.psql import DBSession, Base, engine

session = DBSession()


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


Base.metadata.create_all(engine)


def apply_limit_offset(query, sort_column_object=None, page=None, size=None):
    # Always descending
    if type(sort_column_object) is list:
        query = query.order_by(*[desc(x) for x in sort_column_object])
    else:
        query = query.order_by(desc(sort_column_object))

    if page and size:
        page = int(page)
        size = int(size)
        offset = page * size
        query = query.limit(size).offset(offset)

    return query


def search_model(query_string, bigg_id_sim_cutoff=0.2, page=None, size=None):
    sim_bigg_id = func.similarity(Model.bigg_id, query_string)
    # sort_column_object = Model.bigg_id
    query = (session
             .query(Model.bigg_id, Model.django_orm_id)
             .filter(sim_bigg_id >= bigg_id_sim_cutoff)
             )
    # query = apply_limit_offset(query, sort_column_object)
    # return [{'bigg_id': o[0]} for o in query]
    return query


def count_search_model_result(query_string, bigg_id_sim_cutoff):
    sim_bigg_id = func.similarity(Model.bigg_id, query_string)
    query = (session
             .query(Model.bigg_id)
             .filter(sim_bigg_id >= bigg_id_sim_cutoff)
             )
    return query.count()


def search(query_string, model,
           bigg_id_sim_cutoff=0.2, name_sim_cutoff=0.3,
           page=None, size=None):
    if model.__name__ == 'Model':  # Model.__name__:
        return search_model(query_string, bigg_id_sim_cutoff, page, size)
    sim_bigg_id = func.similarity(model.bigg_id, query_string)
    sim_name = func.similarity(model.name, query_string)

    # sort_column_object = func.greatest(sim_bigg_id, sim_name)

    # Always order by the greater similarity
    query = (session
             .query(model.bigg_id, model.name, model.django_orm_id)
             .filter(or_(sim_bigg_id >= bigg_id_sim_cutoff,
                         and_(sim_name >= name_sim_cutoff,
                              model.name != '')))
             )

    # query = apply_limit_offset(query, sort_column_object, page, size)

    # return [{'bigg_id': o[0], 'name':[1]} for o in query]
    return query


def count_search_result(query_string, model, bigg_id_sim_cutoff=0.2, name_sim_cutoff=0.3):
    if model.__name__ == 'Model':  # Model.__name__:
        return count_search_model_result(query_string, bigg_id_sim_cutoff)
    sim_bigg_id = func.similarity(model.bigg_id, query_string)
    sim_name = func.similarity(model.name, query_string)
    query = (session
             .query(model.bigg_id, model.name)
             .filter(or_(sim_bigg_id >= bigg_id_sim_cutoff,
                         and_(sim_name >= name_sim_cutoff,
                              model.name != '')))
             )
    return query.count()
