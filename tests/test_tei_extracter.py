from tei_extracter import extract_indices


def test_extracter():
    entities = extract_indices("data/generalemissiven_8_content_pagina-255-image.tei.xml")
    assert len(entities) > 0
    assert entities[0] == 'Acapulco'
