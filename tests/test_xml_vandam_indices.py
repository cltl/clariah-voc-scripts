from xml_vandam_indices import extract

INFILE = 'data/tests/vandam-indices.xml'


def test_vandam_indices():
    indices = extract(INFILE)
    assert len(indices) == 3
    assert indices[0] == 'Pieter van Dam'
    assert indices[1] == 'Dr. G.W. Th. baron van Boetzelaar van Asperen en Dubbeldam'
    assert indices[2] == 'Boetzelaar van Asperen en Dubbeldam'
