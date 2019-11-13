import pytest

from vandam_extracter import extract, normalize_page, body, find_path, docid, element_paths
IN_FILE = 'data/vandam_extract.xml'


def test_page_extraction():
    assert docid(IN_FILE) == 'vandam:vol4'
    pages = extract(IN_FILE)
    assert len(pages) == 3


def test_subsumed_elts():
    bd = body(IN_FILE)

    paths = element_paths(bd)
    assert 'body -> div1 -> div2 -> p -> note -> p -> lb' in paths
    assert find_path(bd, ['p', 'note'])
    assert find_path(bd, ['p', 'pb'])
    assert not find_path(bd, ['note', 'pb'])


def test_norm_page():
    p = '4'
    max = 298
    assert normalize_page(p, max) == '004'