from haystack.query import SearchQuerySet, SQ
from biobricks.models import Biobrick
import functools
import random


def search_biobricks(*keywords, num=5):
    if Biobrick.objects.count() < num:
        return sr2obj(Biobrick.objects.all())

    if not keywords:
        return fill_in([], num)

    sq = functools.reduce(lambda a, b: a | b, (SQ(content__fuzzy=keyword) for keyword in keywords))
    sqs = SearchQuerySet().models(Biobrick).filter(sq).order_by('-_score')

    count = sqs.count()
    if count < num:
        return fill_in(sr2obj(sqs), num)
    else:
        return sr2obj(sqs[0:num])


def fill_in(initial, num):
    """
    return a list filled with initial data and random objects until reaching size of `num`
    """
    biobricks = Biobrick.objects.all()
    result = initial[:]

    while len(result) < num:
        random_obj = random.choice(biobricks)
        if random_obj not in result:
            result.append(random_obj)

    return result


def sr2obj(srs):
    return [sr.object for sr in srs]
