from pretei_gm_extracter import paragraph_strings, process
from utils.tei_xml import parse, with_paragraphs

IN_FILE = "data/tests/generalemissiven_8_content_pagina-255-image.tei.xml"
PB_FILE = "data/tests/gm_8_V.tei.xml"


def test_paragraphs():
    paragraphs = paragraph_strings(IN_FILE)
    assert len(paragraphs) == 37
    assert paragraphs[0] == '255'


def test_file_without_words():
    paras = paragraph_strings(PB_FILE)
    assert len(paras) == 12


def test_tei_text():
    tree = with_paragraphs(IN_FILE, paragraph_strings(IN_FILE))
    assert tree.getroot().findall(".//p")[0].text == "255"

    res = process(IN_FILE, 'data/gm8_255_newp.tei.out')
    assert res
