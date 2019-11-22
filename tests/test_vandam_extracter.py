from utils.tei_tree import NEXT_PAGE_FLAG, PREVIOUS_PAGE_FLAG
from utils.tei_xml import docid
from vandam_extracter import extract_pages, normalize_page

IN_FILE = 'data/tests/vandam_extract.xml'
PB_FILE = 'data/tests/vandam_23_p570.xml'

def test_tei_collection():
    pages = extract_pages(IN_FILE)
    assert len(pages) == 3
    page, paragraphs = pages[0]
    assert page == '4'
    assert len(paragraphs) == 8
    page, paragraphs = pages[1]
    assert page == '5'
    assert len(paragraphs) == 19
    page, paragraphs = pages[2]
    assert page == '6'
    assert len(paragraphs) == 17


def test_paragraphs_across_page_breaks():
    pages = extract_pages(IN_FILE)
    assert len(pages) == 3
    page, paragraphs = pages[0]
    assert paragraphs[5].endswith("drie jaren de {}".format(NEXT_PAGE_FLAG))
    page, paragraphs = pages[1]
    assert paragraphs[0].startswith('{} Compagnie'.format(PREVIOUS_PAGE_FLAG))
    assert paragraphs[6].endswith(' vertreckende {}'.format(NEXT_PAGE_FLAG))
    page, paragraphs = pages[2]
    assert paragraphs[8].startswith('{} schepen'.format(PREVIOUS_PAGE_FLAG))


def test_line_breaks():
    pages = extract_pages(IN_FILE)
    page, paragraphs = pages[2]
    assert "Augustus 1617" in paragraphs[2]
    assert "1 April" in paragraphs[7]
    assert "en andere daartoe" in paragraphs[8]
    assert "de Classes" in paragraphs[13]


def test_page_extraction():
    assert docid(IN_FILE) == 'vandam:vol4'


def test_norm_page():
    p = 4
    max = 298
    assert normalize_page(p, max) == '004'


def test_no_superfluous_page_break_markers():
    pages = extract_pages(PB_FILE)
    assert len(pages) == 2
    assert len(pages[0][1]) == 10

