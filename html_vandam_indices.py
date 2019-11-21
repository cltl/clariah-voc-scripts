"""Extracts indices from html-derived files for vandam

Expects input files with two entries per line (lines are marked '<br>' tags).
Entries are cleaned up and filtered, notably to remove page numbers and discard titles and comments.
Entries that have comma-separated parts are reordered, and alternative forms (marked by parentheses) are extracted.
"""

import itertools
import sys
import glob
import re
from index_page_extracter import flatmap, in_paren_vars, ext_paren_vars


def clean(s):
    s = re.sub(r"[,]* [0-9]+.*", "", s)     # removes pages
    s = re.sub(r"[, \(]*zie.*", "", s)      # removes additional references
    s = re.sub(r"[, \(]*ook.*", "", s)      # removes additional references
    s = re.sub(r",$", "", s)                # removes final comma
    s = s.replace('•', '')                  # found in Locations index
    return s


def validate_raw_entry(s):
    is_index_title = s.isupper()
    is_section_character = re.match(r"[A-Z]\.", s)
    is_page_number = re.match(r"[0-9]+\W*", s)
    is_non_word = re.match(r"\W+", s)
    if is_index_title or is_section_character or is_page_number or is_non_word:   # or re.match(r"\s+", s) or s.isdigit()
        return ""
    else:
        return s


def get_parts(s):
    parts = s.split(", ")
    if len(parts) > 3:
        return []
    elif len(parts) == 3:
        if parts[-1].startswith('('):
            parts = [parts[1]] + [parts[0]]  # removes additional references
        elif 'van' in parts[-1]:
            parts = parts[1:] + [parts[0]]
        else:
            parts = [parts[1]] + [parts[0]] + [parts[2]]
    else:
        parts.reverse()
    return parts


def variants(p):
    """Extracts variants for an entry part.

    character entries (len == 1) and long entries (comments) are excluded"""
    return [v for v in flatmap(in_paren_vars, ext_paren_vars(p)) if 1 < len(v) < 50]


def variant_parts(s):
    s = validate_raw_entry(clean(s))
    if not s:
        return []
    return [variants(p) for p in get_parts(s)]


def combinations(var_parts):
    if not var_parts:
        return []
    current = var_parts[-1]
    all_combinations = [[c] for c in current]

    i = len(var_parts) - 2
    while i >= 0:
        if i == len(var_parts) - 2:
            current = product(var_parts[i], current)
        else:
            current = product_fold(var_parts[i], current)
        all_combinations.extend(current)
        i -= 1

    return [" ".join(p) for p in all_combinations]


def product_fold(list1, list2):
    return [[e[0]] + e[1] for e in itertools.product(list1, list2)]


def product(list1, list2):
    return [list(e) for e in itertools.product(list1, list2)]


def process_entry(s):
    return combinations(variant_parts(s))


def process_line_vol4(line):
    """Extracts candidate entries from each line"""
    return flatmap(process_entry, re.split(r"\s\s+", line))


def process_file_vol4(file):
    return flatmap(process_line_vol4, open(file, 'r').read().split('<br>'))


def extract(indir):
    return flatmap(process_file_vol4, glob.glob('{}/*'.format(indir)))


def process_line(entry_extracter):
    def process(line):
        return flatmap(entry_extracter, re.split(r"\s\s+", line))
    return process


def process_file(entry_extracter):
    def process(file):
        return flatmap(process_line(entry_extracter), open(file, 'r').read().split('<br>'))
    return process


def extract_entries(indir, volume):
    if volume == '4':
        return flatmap(process_file(process_entry), glob.glob('{}/*'.format(indir)))
    else:
        return flatmap(process_file(lambda x: [validate_raw_entry(clean(x))]), glob.glob('{}/*'.format(indir)))


def write(indices, label, outfile):
    with open(outfile, 'w') as f:
        f.write('\n'.join(["{}\t{}".format(i, label) for i in indices]))


def parenthesis_variants(s):
    paren_vars = ext_paren_vars(s)
    if len(paren_vars) > 1:
        return [paren_vars[0], "{} {}".format(paren_vars[1], paren_vars[0])]
    return paren_vars


def is_shipname_marker(s):
    return 'schip' in s or 'boot' in s


def is_location_marker(s):
    return 'kaap' in s or 'eiland' in s or 'vesting' in s or 'fort' in s


def infer_label(entry):
    paren_vars = ext_paren_vars(entry)
    if len(paren_vars) > 1:
        if is_shipname_marker(paren_vars[1]):
            return "{}\tSHP".format(paren_vars[0])
        elif is_location_marker(paren_vars[1]):
            return "{}\tLOC".format(paren_vars[0])
    return "{}\tOTH".format(paren_vars[0])


def add_labels(entries, volume, label):
    if volume == '4':
        return ["{}\t{}".format(i, label) for i in entries]
    elif label == 'PER':
        entries = flatmap(parenthesis_variants, entries)
        return ["{}\t{}".format(i, label) for i in entries if i]
    else:
        return [infer_label(i) for i in entries if i]


def extract(volume, indir, label, outfile):
    entries = extract_entries(indir, volume)
    with open(outfile, 'w') as f:
        f.write('\n'.join([e for e in add_labels(entries, volume, label)]))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage:")
        print("python vandam_indices.py {volume} {indir} {NE-type} {outfile}")
        exit(1)
    extract(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

