"""Functions for processing TEI files with lxml.etree"""

from lxml import etree

TEI_NS = "http://www.tei-c.org/ns/1.0"
LB = 'lb'
PB = 'pb'
P = 'p'
NOTE = 'note'
HEAD = 'head'


def parse(file):
    return etree.parse(file)


def root(file):
    return parse(file).getroot()


def body(infile):
    return root(infile).find(tei_path('body'))


def text(infile):
    return root(infile).find(tei_path('text'))

def docid(infile):
    return root(infile).find(tei_path('idno')).text


def words_from_file(infile):
    return [e.text for e in root(infile).findall(".//w")]


def words(elem):
    return [e.text for e in elem.findall(".//w") if e.text is not None]


def paragraphs(infile):
    return [p for p in root(infile).findall(".//p")]


def highlighted(elem):
    return [e for e in elem.findall(".//hi")]


def names(infile):
    return [e.text for e in root(infile).iter('fullname', 'surname')]


def with_paragraphs(infile, paragraphs):
    tree = parse(infile)
    text = tree.getroot().find(".//text")
    body = text.find(".//body")
    body.getparent().remove(body)
    newbody = etree.SubElement(text, "body")
    for p in paragraphs:
        etree.SubElement(newbody, "p").text = p
    return tree


def tei_tag(tag):
    return "{{{}}}{}".format(TEI_NS, tag)


def tei_path(tag):
    x = ".//{{{}}}{}".format(TEI_NS, tag)
    return x


def untag(tag):
    try:
        return tag.replace("{{{}}}".format(TEI_NS), "")
    except AttributeError:
        print("AttributeError trying to untag: {}".format(tag))
        return tag


def is_page_break(elem):
    return elem.tag == PB


def is_paragraph(elem):
    return elem.tag == P


def is_note(elem):
    return elem.tag == NOTE


def is_head(elem):
    return elem.tag == HEAD


def is_line_break(elem):
    return elem.tag == LB
