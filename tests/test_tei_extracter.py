from index_page_extracter import word_sequences, extract, variants, gazetteer_items, tei_paragraphs
from collection_extracter import LABEL


IN_FILE = "data/tests/generalemissiven_8_content_pagina-255-image.tei.xml"


def test_variants():
    test_string0 = "Ajengo(a)"
    test_string1 = "Delftse  Poort  (Colombo)"
    test_string2 = "Porca(d),  Vorst  van"
    test_string3 = "Vries, Menno de, zie Sents, Menno de, Vries, Jacob de"
    result0 = ['Ajengoa', 'Ajengo']
    result1 = ['Delftse Poort', 'Colombo']
    result2 = ['Porcad', 'Vorst van Porcad', 'Porca', 'Vorst van Porca']
    result3 = ['Vries', 'Menno de Vries']

    assert variants(test_string0) == result0
    assert variants(test_string1) == result1
    assert variants(test_string2) == result2
    assert variants(test_string3) == result3


def test_word_sequences():
    seq = ['255', 'INDEX', 'VAN', 'GEOGRAFISCHE', 'NAMEN', 'Acapulco', '130,', '233', 'Adonara', '135']
    assert word_sequences(seq) == ['Acapulco', 'Adonara']


def test_gazetteer_items():
    items = gazetteer_items(IN_FILE)
    assert items[0] == 'Acapulco'


def test_extracter():
    out_file = "data/gm8_255.lex"
    extract(IN_FILE, LABEL['locations'], out_file)

    i = 0
    with open(out_file, 'r') as f:
        for line in f:
            if i == 0:
                assert line == "Acapulco\t{}\n".format(LABEL['locations'])
            elif i == 1:
                assert line == "Adonara\t{}\n".format(LABEL['locations'])
            else:
                break
            i += 1


def test_paragraphs():
    paragraphs = tei_paragraphs(IN_FILE)
    assert len(paragraphs) == 10
