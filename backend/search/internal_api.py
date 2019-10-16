from haystack.query import SearchQuerySet, SQ
from biobricks.models import Biobrick
import functools
import random


def search_biobricks(*keywords, num=5):
    if Biobrick.objects.count() < 5:
        return sr2obj(Biobrick.objects.all())

    if not keywords:
        return fill_with_randoms([], num)

    sq = functools.reduce(lambda a, b: a | b, (SQ(content__fuzzy=keyword) for keyword in keywords))
    sqs = SearchQuerySet().models(Biobrick).filter(sq).order_by('-_score')

    count = sqs.count()
    if count < 5:
        return fill_with_randoms(sr2obj(sqs), 5 - count)
    else:
        return sr2obj(sqs[0:5])


def fill_with_randoms(initial, num):
    count = Biobrick.objects.count()
    result = initial[:]

    while len(result) < 5:
        random_obj = Biobrick.objects.get(id=random.randint(1, count))
        if random_obj not in result:
            result.append(random_obj)

    return result


def sr2obj(srs):
    return [sr.object for sr in srs]
