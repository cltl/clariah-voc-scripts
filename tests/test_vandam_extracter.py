from spacy.data import nl_core_news_sm

from vandam_extracter import extract_pages, tokenizer
IN_FILE = 'data/vandam-4.xml'


def test_page_extraction():
    docid, pages = extract_pages(IN_FILE, tokenizer(nl_core_news_sm.load()))
    assert docid == 'vandam:vol4'
    assert len(pages) == 286
