from .models import TrgmSimilarity
from django.db.models import QuerySet, F, Q, Value, FloatField
from django.db.models.functions import Greatest


class SimilarityQuery:
    def __init__(self, query_strings=None, query_model=None, filter_list=None, ordered_query=False, limit=0):
        self.query_strings = query_strings or []
        self.query_model = query_model
        self.filter_list = filter_list or []
        self.ordered_query = ordered_query
        self.size_limit = limit

    def query(self, *query_strings):
        clone = self._clone()

        clone.query_strings.extend(query_strings)
        return clone

    def model(self, stuff):
        clone = self._clone()

        clone.query_model = stuff
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

        clone.size_limit = limit
        return clone

    def count(self):
        query = self.load_query()
        return query.count()

    def load_query(self):
        filter_query = None
        query_strings = self.query_strings or ['']
        qs = self.query_model.objects

        sort_field = []
        for entry, threshold in self.filter_list:
            for c, query_string in enumerate(query_strings):
                field = '_'.join([entry, str(c), 'score'])
                sort_field.append(field)
                qs = qs.annotate(**{
                    field: TrgmSimilarity(F(entry), Value(query_string))
                })

                if filter_query is None:
                    filter_query = Q(**{
                        field + '__gte': threshold
                    }) & ~Q(**{entry: Value('')})
                else:
                    filter_query = filter_query | Q(**{
                        field + '__gte': threshold
                    }) & ~Q(**{entry: Value('')})

        qs = qs.filter(filter_query)
        if self.ordered_query:
            if len(sort_field) > 1:
                qs = qs.annotate(greatest_score=Greatest(
                    *sort_field, output_field=FloatField())).order_by('-greatest_score')
            elif len(sort_field) == 1:
                qs = qs.order_by(sort_field[0])
            else:
                raise RuntimeError('No entry or query_string found')
        if self.size_limit:
            qs = qs[:self.size_limit]
        return qs

    def _clone(self, klass=None):
        if klass is None:
            klass = self.__class__

        clone = klass(self.query_strings, self.query_model,
                      self.filter_list, self.ordered_query, self.size_limit)
        return clone
