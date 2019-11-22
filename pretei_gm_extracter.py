"""Text Extraction of Generale Missiven from pre-TEI files"""
import sys

from lxml import etree
from utils.tei_xml import parse, with_paragraphs, paragraphs, highlighted, words


def line_string(line):
    newl = " ".join(words(line))
    if newl.endswith("-") or newl.endswith('¬'):
        newl = newl[:-1]
    return newl


def paragraph_string(para):
    return " ".join(line_string(line) for line in highlighted(para))


def paragraph_strings(infile):
    return [paragraph_string(p) for p in paragraphs(infile)]


def extract(in_file, out_file):
    with open(out_file, 'w') as f:
        for p in paragraph_strings(in_file):
            f.write("{}\n".format(p))


def process(in_file, out_file):
    tree = with_paragraphs(in_file, paragraph_strings(in_file))
    tree_string = etree.tounicode(tree, pretty_print=True)
    with open(out_file, 'w') as f:
        f.write(tree_string)
    return tree_string


def replace_paragraphs(in_file):
    paras = paragraph_strings(in_file)    # extracts paragraphs before modifying the tree...
    tree = parse(in_file)
    text = tree.getroot().find(".//text")
    body = text.find(".//body")
    body.getparent().remove(body)
    newbody = etree.SubElement(text, "body")
    for p in paras:
        etree.SubElement(newbody, "p").text = p
    return tree


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python pretei_gm_extracter.py {in_file} {out_file}")
        exit(1)
    process(sys.argv[1], sys.argv[2])
