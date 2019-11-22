"""Index Extraction from a Generale Missiven index page."""

import sys
import re
from utils.func import flatmap
from utils.lexicon import format_entry, ext_paren_vars, in_paren_vars
from utils.tei_xml import words_from_file


def clean(s):
    if s.endswith(','):             # occurs in TEI files
        s = s[:-1]
    if ', zie ' in s:
        s = s.split(', zie ')[0]    # removes ', zie ...' references
    return re.sub(r"  +", " ", s)   # occurs in hOCR files


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
    items = list(set(flatmap(variants, word_sequences(words_from_file(in_file)))))
    items.sort()
    return items


def extract(in_file, label, out_file):
    """Extracts lexicon entries from a TEI input file and writes them out along with their NE label."""
    with open(out_file, 'w') as f:
        for item in gazetteer_items(in_file):
            f.write(format_entry(item, label))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("python gm_index_page.py {tei_file} {NE_type} {out_file}")
        exit(1)
    extract(sys.argv[1], sys.argv[2], sys.argv[3])
