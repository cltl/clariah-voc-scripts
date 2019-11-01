from collection_extracter import load, ne_label, files, extract_lexicon, LABEL, vol_page, page_range

INDICES_CSV = 'data/GM_indices.csv'
TEST_DIR = 'data/tests'


def test_load():
    assert load(INDICES_CSV)[8][LABEL['locations']] == (255, 265)


def test_ne_label():
    indices = load(INDICES_CSV)
    assert ne_label(indices, 8, 260) == LABEL['locations']


def test_files():
    assert vol_page('generalemissiven_6_content_pagina-980-image.tei.xml') == (6, 980)
    assert len(files(TEST_DIR, 8, page_range(load(INDICES_CSV), 8, 'all'))) == 3
    assert files(TEST_DIR, 6, range(980, 981)) == ['data/tests/generalemissiven_6_content_pagina-980-image.tei.xml']


def test_extract_lexicon():
    out_file = 'data/gm8.lex'
    extract_lexicon(TEST_DIR, 8, 'all', out_file)
    with open(out_file, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                assert line == "# volume: 8, pages: all\n"
            elif i == 1:
                assert line == "Acapulco\t{}\n".format(LABEL['locations'])
            elif i == 2:
                assert line == "Adonara\t{}\n".format(LABEL['locations'])
            else:
                break

