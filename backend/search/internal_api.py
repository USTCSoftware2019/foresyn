from biobricks.models import Biobrick
from .common import SimilarityQuery
import functools
import random


def search_biobricks(*keywords, num=5):
    sq = SimilarityQuery()

    sq = (sq.query(*keywords)
          .model(Biobrick)
          .apply_filter_or('part_name', 0.3)
          .apply_filter_or('description', 0.3)
          .apply_filter_or('keywords', 0.3)
          .apply_order()
          .apply_limit(num)
          )

    return sq.load_query()
