from django.db.models import F, Func


class TrgmSimilarity(Func):
    function = 'trgm_similarity'
    template = '%(function)s(%(expressions)s)'

    def as_sqlite(self, *args, **kwargs):
        raise RuntimeError('TrgmSimilarity doesn\'t support sqlite')

    def as_postgresql(self, compiler, connection):
        return self.as_sql(compiler, connection, function='similarity')
