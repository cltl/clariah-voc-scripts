import re

from html_vandam_indices import infer_label, parenthesis_variants, validate_raw_entry, clean, variant_parts, process_file_vol4, process_line_vol4
from utils.lexicon import NE, format_entry

INFILE = 'data/tests/html_vandam_index'


def test_line_to_items():
    line = "Letellier, Michel, 210.                           Ongena, Petrus, 165, 171."
    clean_items = [clean(s) for s in re.split(r"\s\s+", line)]
    assert clean_items == ["Letellier, Michel", "Ongena, Petrus"]

    items = process_line_vol4(line)
    assert items == ["Letellier", "Michel Letellier", "Ongena", "Petrus Ongena"]


def test_variants():
    s = 'Goens, Rijcklof van, Sr.'
    parts = variant_parts(s)
    assert parts == [['Rijcklof van'], ['Goens'], ['Sr.']]

    s = 'Homer, C , (w.s. C. Zomer)'
    assert variant_parts(s) == [['C '], ['Homer']]


def test_html_vandam_index_extraction():
    indices = process_file_vol4(INFILE)
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


def test_volume_index_3():
    e_per = "Coeck (Jan), zie Koek."
    s = validate_raw_entry(clean(e_per))
    variants = parenthesis_variants(s)
    assert variants == ['Coeck', 'Jan Coeck']

    e_shp = "Gelderlant (schip), 475."
    s = validate_raw_entry(clean(e_shp))
    assert infer_label(s) == format_entry('Gelderlant', NE.SHP.name)



