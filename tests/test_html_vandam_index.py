import re

from html_vandam_indices import extract_items_from_lines, extract_index_items, clean, clean_variant_parts

INFILE = 'data/html_vandam_index'


def test_line_to_items():
    line = "Letellier, Michel, 210.                           Ongena, Petrus, 165, 171."
    clean_items = [clean(s) for s in re.split(r"\s\s+", line)]
    assert clean_items == ["Letellier, Michel", "Ongena, Petrus"]

    items = extract_index_items(line)
    assert items == ["Letellier", "Michel Letellier", "Ongena", "Petrus Ongena"]


def test_variants():
    s = 'Goens, Rijcklof van, Sr.'
    parts = clean_variant_parts(s)
    assert parts == [['Rijcklof van'], ['Goens'], ['Sr.']]

    s = 'Homer, C , (w.s. C. Zomer)'
    assert clean_variant_parts(s) == [['C '], ['Homer']]

def test_html_vandam_index_extraction():
    indices = extract_items_from_lines(INFILE)
    # name1 = "Kalero, Marcus, zie Laleio"
    assert "Marcus Kalero" in indices
    assert "zie Laleio Marcus Kalero" not in indices
    assert "Kalero" in indices
    # name2 = "Maes (Masius), Marcus"
    assert "Maes" in indices
    assert "Masius" in indices
    assert "Marcus Maes" in indices
    assert "Marcus Masius" in indices
    # name = "Oudshoorn van Sonneveld, H. V."
    assert "Oudshoorn van Sonneveld" in indices
    assert "H. V. Oudshoorn van Sonneveld" in indices


