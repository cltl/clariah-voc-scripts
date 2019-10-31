import re
from itertools import chain


in_paren = r"([^(]*\S)\((.*)\)(.*)"  #Ajengo(a)
ext_paren = r"([^(]*) \((.*)\)"       #Delftse  Poort  (Colombo)




def resolve_ext_paren(s):
    m = re.search(ext_paren, s)
    if m is not None:
        return [m.group(1), m.group(2)]
    else:
        return [s]


def resolve_in_paren(s):
    m = re.search(in_paren, s)
    if m is not None:
        return ["{}{}{}".format(m.group(1), m.group(2), m.group(3)), "{}{}".format(m.group(1), m.group(3))]
    else:
        return [s]


def invert_comma_separated(s):
    if ", " in s:
        parts = s.split(", ")
        parts.reverse()
        return [parts[-1], " ".join(parts)]
    else:
        return [s]


def clean_string(s):
    if s.endswith(','):
        s = s[:-1]
    return re.sub(r"  +", " ", s)


def flatten(list_of_lists):
    return list(chain.from_iterable(list_of_lists))


def flatmap(fct, lst):
    return flatten(map(fct, lst))


def reformat(s):
    return flatmap(invert_comma_separated, flatmap(resolve_in_paren, resolve_ext_paren(clean_string(s))))



