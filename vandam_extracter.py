import pathlib
import re
import sys
import time

from KafNafParserPy import KafNafParser
from lxml import etree
from KafNafParserPy.header_data import CHeader, CfileDesc, Clp
import tei_extracter as tei

TEI_NS = "http://www.tei-c.org/ns/1.0"


def tei_tag(tag):
    return "{{{}}}{}".format(TEI_NS, tag)


def tei_path(tag):
    x = ".//{{{}}}{}".format(TEI_NS, tag)
    return x


def untag(tag):
    return tag.replace("{{{}}}".format(TEI_NS), "")


def text_and_tail(elt):
    text = ''
    if elt.text:
        text += elt.text
    if elt.tail:
        text += elt.tail
    return re.sub(r"\s+", " ", text).strip()


def clean_line_break(all_text):
    if all_text.endswith(' -'):
        return all_text[:-2]
    elif all_text.endswith('-'):
        return all_text[:-1]
    else:
        return all_text + ' '


def get_paragraph_text(elt):
    res = [text_and_tail(t) for t in elt.iter()]
    res = [clean_line_break(t) for t in res if t]
    return ''.join(res)     # + '\n'


def get_note_text(elt):
    return get_paragraph_text(elt)


def get_paragraph_text_across_page_break(elt):
    """ gets the text content of a paragraph and that of included notes
    :param elt:
    :return:
    """
    notes = []
    page_nb = -1
    content = []
    for child in elt:
        if untag(child.tag) == 'note':
            notes.append(get_note_text(child))
        else:
            content.extend([text_and_tail(t) for t in child.iter()])
            if untag(child.tag) == 'pb':
                page_nb = child.attrib['n']
    text = ''.join([clean_line_break(t) for t in content if t])

    fragments = [text]
    fragments.extend(notes)
    return fragments, page_nb


def get_text(elt, pages, fragments, current_page):
    if untag(elt.tag) == 'head':
        fragments.append(elt.text)
    elif untag(elt.tag) == 'note':
        fragments.append(get_note_text(elt))
    elif untag(elt.tag) == 'pb':
        if fragments:
            pages.append((current_page, fragments))
            fragments = []
        current_page = elt.attrib['n']
    elif untag(elt.tag) == 'p':
        if elt.findall(tei_path('pb')):
            p_str, next_page = get_paragraph_text_across_page_break(elt)
            fragments.extend(p_str)
            pages.append((current_page, fragments))
            fragments = []
            current_page = next_page
        else:
            fragments.append(get_paragraph_text(elt))
    else:
        for child in elt:
            pages, fragments, current_page = get_text(child, pages, fragments, current_page)
    return pages, fragments, current_page


def extract(infile):
    """extracts all paragraph-like fragments (head, paragraphs, notes) per page"""

    element = body(infile)
    pages = []
    fragments = []
    current_page = 1
    for child in element:
        pages, page_str, current_page = get_text(child, pages, fragments, current_page)
    if fragments:
        pages.append((current_page, fragments))
    return pages


def get_context(infile):
    tree = etree.parse(infile)
    text = tree.getroot().find(tei_path('text'))
    text.getparent().remove(text)
    text = etree.SubElement(tree.getroot(), tei_tag("text"))
    newbody = etree.SubElement(text, tei_tag("body"))
    return tree, newbody


def replace_paragraphs(infile):
    pages = extract(infile)   # extracts paragraphs before modifying the tree...

    trees = []
    for p, fragments in pages:
        tree, newbody = get_context(infile)
        for f in fragments:
            etree.SubElement(newbody, tei_tag("p")).text = f + '\n\n'
        trees.append((p, tree))
    return trees


def body(infile):
    return tei.parse(infile).getroot().find(tei_path('body'))


def docid(infile):
    return tei.parse(infile).getroot().find(tei_path('idno')).text


def find_path(element, path_list):
    """finds a subpath in the element tree.

    Note: expects a contiguous subpath"""
    subpath = ' -> '.join(path_list)
    return any(subpath in p for p in element_paths(element))


def element_paths(element):
    """extracts all paths in the element tree"""
    paths = list(tree_paths(element))
    paths.sort()

    return paths


def tree_paths(element):
    paths = set()
    t = untag(element.tag)
    for child in element:
        paths.update('{} -> {}'.format(t, p) for p in tree_paths(child))
    if not paths:
        paths.add(t)
    return paths


def normalize_page(p, max):
    nb_digits_max = len(str(max))
    nb_digits = len(p)
    pfx = ['0'] * (nb_digits_max - nb_digits)
    return ''.join(pfx) + p


def write(docid, pages, outdir, sfx):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    if sfx == 'tei':
        for p, tree in pages:
            with open("{}/{}_{}.tei".format(outdir, docid, normalize_page(p, len(pages))), 'w') as f:
                f.write(etree.tounicode(tree, pretty_print=True))
    elif sfx == 'naf':
        for p, fragments in pages:
            naf = create_naf_from_item('{}_{}'.format(docid, normalize_page(p, len(pages))), '\n\n'.join(fragments))
            naf.dump("{}/{}_{}.naf".format(outdir, docid, p))
    elif sfx == 'text':
        for p, fragments in pages:
            with open("{}/{}_{}.txt".format(outdir, docid, normalize_page(p, len(pages))), 'w') as f:
                f.write('\n\n'.join(fragments))


def create_naf_from_item(title, content):
    naf = KafNafParser(type="NAF")
    naf.set_version("3.0")
    naf.set_language("nl")
    naf.set_header(create_header(title))
    naf.add_linguistic_processor('raw', create_linguistic_processor())
    naf.set_raw(content)
    return naf


def create_header(title):
    header = CHeader(type="NAF")
    file_desc = CfileDesc()
    file_desc.set_creationtime(time.strftime('%Y-%m-%dT%H:%M:%S%Z'))
    file_desc.set_title(title)
    header.set_fileDesc(file_desc)
    return header


def create_linguistic_processor():
    lp = Clp()
    lp.set_name('data prep inception')
    lp.set_version("1.0")
    lp.set_timestamp()
    return lp


def tokenizer(model):
    def apply(text):
        return " ".join(token.text for token in model(text))
    if model is not None:
        return apply
    else:
        return lambda x: x


def process(infile, outdir, format):
    if format == 'tei':
        write(docid(infile), replace_paragraphs(infile), outdir, sfx=format)
    else:
        write(docid(infile), extract(infile), outdir, sfx=format)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage:")
        print("python vandam_extracter.py {infile} {outdir} {format}")
        exit(1)
    process(sys.argv[1], sys.argv[2], sys.argv[3])
