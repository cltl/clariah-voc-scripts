"""Person Index extraction from Van Dam *.namen.xml files."""
import sys

import re

from utils.tei_xml import names
from utils.lexicon import format_entry, NE


def clean(txt):
    return re.sub(r"\s+", " ", txt)


def extract(infile):
    return [clean(n) for n in names(infile) if n is not None]


def write(indices, outfile):
    with open(outfile, 'w') as f:
        for i in indices:
            f.write(format_entry(i, NE.PER.name))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python xml_vandam_indices.py {infile} {outfile}")
        exit(1)
    write(extract(sys.argv[1]), sys.argv[2])
