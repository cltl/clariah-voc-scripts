import sys

from lxml import etree


def line_string(line):
    newl = " ".join(w.text for w in line.findall(".//w") if w.text is not None)
    if newl.endswith("-") or newl.endswith('¬'):
        newl = newl[:-1]
    return newl


def paragraph_string(para):
    return " ".join(line_string(line) for line in para.findall(".//hi"))


def paragraph_strings(tree):
    return [paragraph_string(p) for p in tree.getroot().findall(".//p")]


def extract(in_file, out_file):
    with open(out_file, 'w') as f:
        f.write("\n".join(p for p in paragraph_strings(etree.parse(in_file))))


def add_root_attributes_and_docinfo(tree):
    """FIXME find how to add attributes with prefixes"""
    attribs = tree.getroot().attrib
    attribs['xmnls'] = "http://www.tei-c.org/ns/1.0"
    # attribs['xmlns:egXML'] = "http://www.tei-c.org/ns/Examples"
    return tree


def process(in_file, out_file):
    #tree = replace_paragraphs(add_root_attributes_and_docinfo(etree.parse(in_file)))
    tree = replace_paragraphs(etree.parse(in_file))
    tree_string = etree.tounicode(tree, pretty_print=True)
    with open(out_file, 'w') as f:
        # f.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')  # added by bash script
        f.write(tree_string)
    return tree_string


def replace_paragraphs(tree):
    paras = paragraph_strings(tree)    # extracts paragraphs before modifying the tree...

    text = tree.getroot().find(".//text")
    body = text.find(".//body")
    body.getparent().remove(body)
    newbody = etree.SubElement(text, "body")
    for p in paras:
        etree.SubElement(newbody, "p").text = p
    return tree


def parse(file):
    return etree.parse(file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python tei_extracter.py {in_file} {out_file}")
        exit(1)
    process(sys.argv[1], sys.argv[2])
