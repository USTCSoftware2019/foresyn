from .models import Biobrick
from .psql import SimilarityQuery
import functools
import random


def search_biobricks(*keywords, num=5):
    sq = SimilarityQuery()

    sq = (sq.query(*keywords)
          .entities(Biobrick)
          .apply_filter_or(Biobrick.partname, 0.3)
          .apply_filter_or(Biobrick.description, 0.3)
          .apply_filter_or(Biobrick.keywords, 0.3)
          .apply_order()
          .apply_limit(num)
          )

    return sq.load_query()
