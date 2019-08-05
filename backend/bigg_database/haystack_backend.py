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
            search_kwargs['query']['filtered']['query']['query_string']['fuzziness'] = 2

            # Prevent escape ~ to \~
            # FIXME:
            # Needs a better approach to append '~' to the query without escape it
            search_kwargs['query']['filtered']['query']['query_string']['query'] = \
                search_kwargs['query']['filtered']['query']['query_string']['query'].replace('\\~', '~')
        except KeyError:
            pass
        return search_kwargs
