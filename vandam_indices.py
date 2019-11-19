import sys

import tei_extracter as tei
import re


def clean(txt):
    return re.sub(r"\s+", " ", txt)


def extract(infile):
    tree = tei.parse(infile).getroot()
    return [clean(t.text) for t in tree.iter('fullname', 'surname') if t.text is not None]


def write(indices, outfile):
    with open(outfile, 'w') as f:
        f.write('\n'.join(["{}\tPER".format(i) for i in indices]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python vandam_indices.py {infile} {outfile}")
        exit(1)
    write(extract(sys.argv[1]), sys.argv[2])
