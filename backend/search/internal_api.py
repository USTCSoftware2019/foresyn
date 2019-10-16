from haystack.query import SearchQuerySet, SQ
from biobricks.models import Biobrick
import functools


def search_biobricks(*keywords):
    sq = functools.reduce(lambda a, b: a | b, (SQ(content__fuzzy=keyword) for keyword in keywords))
    return SearchQuerySet().models(Biobrick).filter(sq)
