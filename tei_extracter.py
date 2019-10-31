from lxml import etree
from gazetteer import reformat


def is_digit(w):
    return w.replace(',', '').isdigit()


def filter_entities(w_elem_text):
    """Extracts word sequences from alternated sequences of words and page numbers."""
    word_seqs = []
    ws = []
    for w in w_elem_text:
        if is_digit(w):
            if ws:
                word_seqs.extend(reformat(" ".join(ws)))
                ws = []
        elif not w.isupper():       # excludes INDEX VAN ...
            ws.append(w)
    return word_seqs


def extract_indices(file):
    return filter_entities([e.text for e in etree.parse(file).getroot().findall(".//w")])


def extract_lexicon(in_file, label, out_file):
    with open(out_file, 'w') as f:
        for mention in extract_indices(in_file):
            f.write("{}\t{}\n".format(mention, label))


