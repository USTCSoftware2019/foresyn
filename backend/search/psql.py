from sqlalchemy import Column, Integer, String, and_, desc, func, or_

from backend.psql import Base, DBSession, engine

from .models import Model

session = DBSession()


Base.metadata.create_all(engine)


class SimilarityQuery:
    def __init__(self, query_strings=None, query_list=None, filter_list=None, ordered_query=False, limit=0):
        self.query_strings = query_strings or []
        self.query_list = query_list or []
        self.filter_list = filter_list or []
        self.ordered_query = ordered_query
        self.size_limit = limit

    def query(self, *query_strings):
        clone = self._clone()

        for query_string in query_strings:
            clone.query_strings.append(query_string)

        return clone

    def entities(self, *stuff):
        clone = self._clone()

        stuff = filter(None, stuff)
        clone.query_list.extend(stuff)
        return clone

    def apply_filter_or(self, entity, threshold=0.2):
        clone = self._clone()

        if entity:
            clone.filter_list.append((entity, threshold))
        return clone

    def apply_order(self):
        clone = self._clone()

        clone.ordered_query = True
        return clone

    def apply_limit(self, limit):
        clone = self._clone()

        clone.limit = limit
        return clone

    def count(self):
        query = self.load_query()
        return query.count()

    def load_query(self):
        filter_query = None
        sim_obj_list = []
        query = session.query(*self.query_list)
        query_strings = self.query_strings or ['']

        for entity, threshold in self.filter_list:
            for query_string in query_strings:
                sim_entity = func.similarity(entity, query_string)
                sim_obj_list.append(sim_entity)
                if filter_query is None:
                    filter_query = (sim_entity >= threshold) & (entity != '')
                else:
                    filter_query = filter_query | \
                        (sim_entity >= threshold) & (entity != '')

        query = query.filter(filter_query)
        if self.ordered_query:
            query = query.order_by(desc(func.greatest(*sim_obj_list)))
        if self.size_limit:
            query = query.limit(self.size_limit)
        return query

    def _clone(self, klass=None):
        if klass is None:
            klass = self.__class__

        clone = klass(self.query_strings, self.query_list,
                      self.filter_list, self.ordered_query, self.size_limit)
        return clone
