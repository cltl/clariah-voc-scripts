"""Text extraction from Van Dam TEI files"""
import pathlib
import sys

from utils.tei_tree import TextTree
from utils import tei_xml as tx


def normalize_page(p, max_pnb):
    nb_digits_max = len(str(max_pnb))
    nb_digits = len(str(p))
    pfx = ['0'] * (nb_digits_max - nb_digits)
    return ''.join(pfx) + str(p)


def file_id(outdir, docname, page_nb, sfx):
    return "{}/{}_{}.{}".format(outdir, docname, page_nb, sfx)


def extract_pages(file):
    tree = TextTree.make(tx.body(file))
    return tree.collect_pages()


def name_files(outdir, docid, sfx, pages):
    max_page = len(pages)
    return [(file_id(outdir, docid, normalize_page(p, max_page), sfx), page) for (p, page) in pages]


def format_page(paragraphs):
    return "\n\n".join(paragraphs)


def process(infile, outdir, sfx='txt'):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    pages = extract_pages(infile)
    for (filename, paragraphs) in name_files(outdir, tx.docid(infile), sfx, pages):
        with open(filename, 'w') as f:
            f.write(format_page(paragraphs))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python vandam_extracter.py {infile} {outdir}")
        exit(1)
    process(sys.argv[1], sys.argv[2])



