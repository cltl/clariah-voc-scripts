import glob
import re
import sys
from functools import reduce
from index_page_extracter import gazetteer_items, format_lexicon_entry


LABEL = {'persons': 'PER', 'ship names': 'SHP', 'locations': 'LOC', 'other': 'OTH'}
VOL_PAGE = r"\D*(\d+)\D*(\d+)\D*"
INDICES_FILE = 'data/GM_indices.csv'


def load(indices_file):
    """Loads a csv file with: volume;label;first-page;last-page.

    Returns a dict: {vol: {label: range(first-page, end-page), ..}, ..}"""
    indices = {}
    with open(indices_file, 'r') as f:
        for i, line in enumerate(f):
            if i > 0:
                items = line.split(";")
                vol, label, pp_start, pp_end = int(items[0]), LABEL[items[1]], int(items[2]), int(items[3]) + 1
                if vol not in indices:
                    indices[vol] = {}
                indices[vol][label] = (pp_start, pp_end)
    return indices


def ne_label(indices, vol, p):
    """Returns a label given a volume and page number"""
    return next(label for (label, pp) in indices[vol].items() if p in range(pp[0], pp[1]))


def vol_page(fname):
    m = re.search(VOL_PAGE, fname)
    if m is not None:
        return int(m.group(1)), int(m.group(2))
    return None


def files(dirname, volume, pages):
    """Filenames matching a volume number and a page range."""
    def fits_vol_page(fname):
        v_p = vol_page(fname)
        return v_p is not None and v_p[0] == volume and v_p[1] in pages

    return [f for f in glob.glob('{}/*_{}_*'.format(dirname, volume)) if fits_vol_page(f)]


def page_range(indices, vol, page_arg):
    if page_arg == 'all':
        pmin = 10000
        pmax = -1
        for (label, pp) in indices[vol].items():
            if pp[0] < pmin:
                pmin = pp[0]
            if pp[1] > pmax:
                pmax = pp[1]
        return range(pmin, pmax)
    elif "-" in page_arg:
        return range(int(page_arg.split('-')[0], int(page_arg.split('-')[1]) + 1))
    else:
        return range(int(page_arg), int(page_arg) + 1)


def extract_lexicon(dirname, volume, page_str, out_file):
    """Extracts a lexicon for all files matching a volume number and a page range."""
    indices = load(INDICES_FILE)
    tei_files = files(dirname, int(volume), page_range(indices, int(volume), page_str))
    with open(out_file, 'w') as fo:
        fo.write("# volume: {}, pages: {}\n".format(volume, page_str))
        for f in tei_files:
            vol, page = vol_page(f)
            for item in gazetteer_items(f):
                fo.write(format_lexicon_entry(item, ne_label(indices, vol, page)))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage:")
        print("python collection_extracter.py {dirname} {volume} {pages:all|x-y} {out_file}")
        exit(1)
    extract_lexicon(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
