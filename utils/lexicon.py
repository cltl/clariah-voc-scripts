"""Patterns and labels for index extraction"""

import re
from enum import Enum

# ------ Patterns ------

IN_PAREN = re.compile(r"([^(]*\S)\((.*)\)(.*)")     # Ajengo(a)
EXT_PAREN = re.compile(r"([^(]*) \((.*)\)")         # Delftse  Poort  (Colombo)
VOL_PAGE = re.compile(r"\D*_(\d+)_\D*(\d+)\D*")       # gm_8_foo_255_bar


def ext_paren_vars(s):
    m = re.search(EXT_PAREN, s)             # ex. Delftse Poort  (Colombo)
    if m is not None:
        return [m.group(1), m.group(2)]     # -> ['Delftse Poort', 'Colombo']
    else:
        return [s]


def in_paren_vars(s):
    m = re.search(IN_PAREN, s)          # ex. Ajengo(a)
    if m is not None:                   # -> ['Ajengoa', 'Ajengo']
        return ["{}{}{}".format(m.group(1), m.group(2), m.group(3)), "{}{}".format(m.group(1), m.group(3))]
    else:
        return [s]


def vol_page(fname):
    m = re.search(VOL_PAGE, fname)                  # ex: gm_8_foo_255_bar
    if m is not None:
        return int(m.group(1)), int(m.group(2))     # -> (8, 255)
    return None


# ------ Index Labels and formatting ------

NE = Enum('NE', ['PER', 'LOC', 'SHP', 'OTH'])


def format_entry(item, label):
    return "{}\t{}\n".format(item, label)


