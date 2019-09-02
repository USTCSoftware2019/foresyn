from haystack.backends.elasticsearch2_backend import Elasticsearch2SearchBackend


class FuzzyBackend(Elasticsearch2SearchBackend):
    def build_search_kwargs(self, query_string, **kwargs):
        search_kwargs = super().build_search_kwargs(
            query_string, **kwargs)
        try:
            # Maybe it is a bug in Lucene before the version 6.2.4
            # Refer to https://github.com/elastic/elasticsearch/issues/23366
            # It does not support the AUTO in fuzziness
            # As for the elasticsearch 2.4.6, the version of Lucene is
            # much lower than 6.2.4
            query_string_length = len(search_kwargs['query']['filtered']['query']['query_string']['query'])
            # Remove '(', ')' and '~' in the query when calculating the length of the querying string
            query_string_length -= 3

            # Refer: https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness
            fuzziness = 2 if query_string_length > 5 else (0 if query_string_length <= 2 else 1)
            search_kwargs['query']['filtered']['query']['query_string']['fuzziness'] = fuzziness

        except KeyError:
            pass
        return search_kwargs
