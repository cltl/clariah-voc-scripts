import gazetteer
import pytest


def test_entity_reformatting():
    test_string0 = "Ajengo(a)"
    test_string1 = "Delftse  Poort  (Colombo)"
    test_string2 = "Porca(d),  Vorst  van"
    result0 = ['Ajengoa', 'Ajengo']
    result1 = ['Delftse Poort', 'Colombo']
    result2 = ['Porcad', 'Vorst van Porcad', 'Porca', 'Vorst van Porca']

    assert gazetteer.reformat(test_string0) == result0
    assert gazetteer.reformat(test_string1) == result1
    assert gazetteer.reformat(test_string2) == result2

