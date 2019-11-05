from tei_extracter import paragraph_strings, replace_paragraphs, parse, add_root_attributes_and_docinfo, process


IN_FILE = "data/tests/generalemissiven_8_content_pagina-255-image.tei.xml"


def test_paragraphs():
    paragraphs = paragraph_strings(parse(IN_FILE))
    assert len(paragraphs) == 37
    assert paragraphs[0] == '255'


def test_file_without_words():
    pb_file = "data/gm_8_V.tei.xml"
    paras = paragraph_strings(parse(pb_file))
    assert len(paras) == 12


def test_tei_text():
    tree = add_root_attributes_and_docinfo(parse(IN_FILE))
    assert tree.getroot().attrib['xmnls'] == "http://www.tei-c.org/ns/1.0"
    assert tree.docinfo.xml_version == '1.0'

    tree = replace_paragraphs(tree)
    assert tree.getroot().findall(".//p")[0].text == "255"

    res = process(IN_FILE, 'data/gm8_255_newp.tei')
    assert res
