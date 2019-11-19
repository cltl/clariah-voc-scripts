# extracts indices from html-like files for vandam
import itertools
import sys
import glob
import re
from index_page_extracter import flatmap, in_paren_vars, ext_paren_vars


def is_valid_variant(p):
    return 1 < len(p) < 50


def variants_part(s):
    return [p for p in flatmap(in_paren_vars, ext_paren_vars(s)) if is_valid_variant(p)]


def is_valid_base_form(s):
    if s.isupper() or s.isdigit() or re.match(r"[A-Z]\.", s) or re.match(r"[0-9]+\W*", s) or re.match(r"\s+", s) or re.match(r"\W+", s):
        return False
    else:
        return True


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


def clean_variant_parts(s):
    s = clean(s)
    if not is_valid_base_form(s):
        return []
    return [variants_part(p) for p in get_parts(s)]


def entry_variants(s):
    vars = clean_variant_parts(s)
    if not vars:
        return []
    combinations = vars[-1]
    all_combinations = [[c] for c in combinations]

    i = len(vars) - 2
    while i >= 0:
        if i == len(vars) - 2:
            combinations = product(vars[i], combinations)
        else:
            combinations = product_fold(vars[i], combinations)
        all_combinations.extend(combinations)
        i -= 1

    return [" ".join(p) for p in all_combinations]


def product_fold(list1, list2):
    return [[e[0]] + e[1] for e in itertools.product(list1, list2)]


def product(list1, list2):
    return [list(e) for e in itertools.product(list1, list2)]


def clean(s):
    s = re.sub(r"[,]* [0-9]+.*", "", s)    # removes pages
    s = re.sub(r"[, \(]*zie.*", "", s)    # removes additional references
    s = re.sub(r"[, \(]*ook.*", "", s)    # removes additional references
    s = re.sub(r",$", "", s)            # removes final comma
    s = s.replace('•', '')              # found in Locations index
    return s


def extract_index_items(line):
    """gets variants from items in line.

    Each line contains at most two items, which need to be validated to exclude character sections (e.g., \'J.\') and
    incomplete forms."""
    return flatmap(entry_variants, re.split(r"\s\s+", line))


def extract_items_from_lines(file):
    return flatmap(extract_index_items, open(file, 'r').read().split('<br>'))


def extract(indir):
    return flatmap(extract_items_from_lines, glob.glob('{}/*'.format(indir)))


def write(indices, label, outfile):
    with open(outfile, 'w') as f:
        f.write('\n'.join(["{}\t{}".format(i, label) for i in indices]))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("python vandam_indices.py {indir} {NE-type} {outfile}")
        exit(1)
    write(extract(sys.argv[1]), sys.argv[2], sys.argv[3])

