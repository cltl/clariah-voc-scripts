"""Text extraction from Van Dam TEI files"""
import argparse
import pathlib
import re
import sys

from utils.tei_tree import TextTree, NEXT_PAGE_FLAG, PREVIOUS_PAGE_FLAG
from utils import tei_xml as tx


def normalize_page(p, max_pnb):
    nb_digits_max = len(str(max_pnb))
    nb_digits = len(str(p))
    pfx = ['0'] * (nb_digits_max - nb_digits)
    return ''.join(pfx) + str(p)


def file_id(outdir, docname, page_nb, sfx):
    return "{}/{}_{}.{}".format(outdir, docname, page_nb, sfx)


def extract_pages(file):
    tree = TextTree.make(tx.text(file))
    return tree.collect_pages()


def name_files(outdir, docid, sfx, pages):
    max_page = len(pages)
    return [(file_id(outdir, docid, normalize_page(p, max_page), sfx), page) for (p, page) in pages]


def format_page(paragraphs):
    return "\n\n".join(paragraphs)


def join_paragraphs(para, next_para):
    para = TextTree.clean_line_break(re.sub(NEXT_PAGE_FLAG, "", para))
    next_para = re.sub(PREVIOUS_PAGE_FLAG, "", next_para)
    return re.sub(r"\s+", " ", "".join([para, next_para]))


def next_goal_origin_pair(pages, start=0):
    goal = None
    for i in range(start, len(pages)):
        for j, para in enumerate(pages[i][1]):
            if para.startswith(PREVIOUS_PAGE_FLAG):
                origin = (i, j)
                if goal is None:
                    raise ValueError(
                        "found previous-page flag at page {}, paragraph {}, but no preceding next-page flag".format(i, j))
                return goal, origin
            if para.endswith(NEXT_PAGE_FLAG):
                goal = (i, j)
                break
    return None, None


def pull_paragraph(pages, goal, origin):
    def paragraph(ij, pp):
        return pp[ij[0]][1][ij[1]]
    pages[goal[0]][1][goal[1]] = join_paragraphs(paragraph(goal, pages), paragraph(origin, pages))
    del pages[origin[0]][1][origin[1]]
    return pages


def regroup_paragraphs(pages):
    (goal, origin) = next_goal_origin_pair(pages)
    while goal is not None:
        pages = pull_paragraph(pages, goal, origin)
        (goal, origin) = next_goal_origin_pair(pages, start=goal[0])
    return pages


def strip_page_breaks(pages):
    def strip_paras(paragraphs):
        return [p.replace(PREVIOUS_PAGE_FLAG, '').replace(NEXT_PAGE_FLAG, '') for p in paragraphs]

    return [(n, strip_paras(ps)) for (n, ps) in pages]


def process(infile, outdir, complete_paragraphs=True, strip_page_markers=True, sfx='txt'):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    pages = extract_pages(infile)
    if complete_paragraphs:
        pages = regroup_paragraphs(pages)
    elif strip_page_markers:
        pages = strip_page_breaks(pages)
    for (filename, paragraphs) in name_files(outdir, tx.docid(infile), sfx, pages):
        with open(filename, 'w') as f:
            f.write(format_page(paragraphs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Text extraction from Van Dam TEI files')
    parser.add_argument('-i', '--in_file', dest='infile', type=str, help='input file')
    parser.add_argument('-o', '--out_dir', dest='outdir', type=str, help='output directory')
    parser.add_argument('-c', '--complete', dest='complete', action='store_true', help="completes paragraphs "
                                                                                       "interrupted by page breaks")
    parser.add_argument('-s', '--strip', dest='strip', action='store_true', help='strips page-break markers')

    args = parser.parse_args()
    process(args.infile, args.outdir, complete_paragraphs=args.complete, strip_page_markers=args.strip)



