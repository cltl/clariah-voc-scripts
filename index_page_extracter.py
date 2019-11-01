import sys
from lxml import etree
import re
from itertools import chain


IN_PAREN = r"([^(]*\S)\((.*)\)(.*)"     #Ajengo(a)
EXT_PAREN = r"([^(]*) \((.*)\)"         #Delftse  Poort  (Colombo)


def clean(s):
    if s.endswith(','):             # occurs in TEI files
        s = s[:-1]
    if ', zie ' in s:
        s = s.split(', zie ')[0]    # removes ', zie ...' references
    return re.sub(r"  +", " ", s)   # occurs in hOCR files


def ext_paren_vars(s):
    m = re.search(EXT_PAREN, s)
    if m is not None:
        return [m.group(1), m.group(2)]
    else:
        return [s]


def in_paren_vars(s):
    m = re.search(IN_PAREN, s)
    if m is not None:
        return ["{}{}{}".format(m.group(1), m.group(2), m.group(3)), "{}{}".format(m.group(1), m.group(3))]
    else:
        return [s]


def comma_inverted_vars(s):
    if ", " in s:
        parts = s.split(", ")
        if len(parts) > 1 and not parts[1].startswith('zie '):
            parts.reverse()
            return [parts[-1], " ".join(parts)]
        else:
            return [parts[0]]
    else:
        return [s]


def flatmap(fct, lst):
    return list(chain.from_iterable(map(fct, lst)))


def variants(s):
    """Cleans an input string and returns a list of variants"""
    return flatmap(comma_inverted_vars, flatmap(in_paren_vars, ext_paren_vars(clean(s))))


def is_page_number_range_or_comma(w):
    return w == ',' or w == '%' or w.replace('.', '').replace(',', '').replace('-', '').replace('%', '').isdigit()


def word_sequences(word_page_seqs):
    """Detects and joins contiguous words in a list of words and page numbers.

    Returns a list of grouped words."""
    w_seqs = []
    ws = []
    for w in word_page_seqs:
        if is_page_number_range_or_comma(w):
            if ws:
                w_seqs.append(" ".join(ws))
                ws = []
        elif not w.isupper():       # excludes INDEX VAN ...
            ws.append(w)
    return w_seqs


def gazetteer_items(in_file):
    """Extracts w elements in a TEI input file and returns lexicon entries with their variants."""
    word_page_seqs = [e.text for e in etree.parse(in_file).getroot().findall(".//w")]
    items = list(set(chain.from_iterable(map(variants, word_sequences(word_page_seqs)))))
    items.sort()
    return items


def format_lexicon_entry(item, label):
    return "{}\t{}\n".format(item, label)


def extract(in_file, label, out_file):
    """Extracts lexicon entries from a TEI input file and writes them out along with their NE label."""
    with open(out_file, 'w') as f:
        for item in gazetteer_items(in_file):
            f.write(format_lexicon_entry(item, label))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("python index_page_extracter.py {tei_file} {NE_type} {out_file}")
        exit(1)
    extract(sys.argv[1], sys.argv[2], sys.argv[3])
