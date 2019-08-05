from haystack.backends.elasticsearch2_backend import Elasticsearch2SearchEngine
from bigg_database.haystack_backend import FuzzyBackend


class FuzzyEngine(Elasticsearch2SearchEngine):
    backend = FuzzyBackend
