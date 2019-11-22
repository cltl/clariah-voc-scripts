import itertools
from itertools import chain


def flatmap(fct, lst):
    return list(chain.from_iterable(map(fct, lst)))


def product(list1, list2):
    return [list(e) for e in itertools.product(list1, list2)]


def product_fold(list1, list2):
    return [[e[0]] + e[1] for e in itertools.product(list1, list2)]
