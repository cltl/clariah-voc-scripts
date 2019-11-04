import sys

from lxml import etree


def tei_paragraphs(in_file):
    paras = [e for e in etree.parse(in_file).getroot().findall(".//p")]

    return list(map(lambda p: " ".join(w.text for w in p.findall(".//w") if w.text is not None), paras))


def extract(in_file, out_file):
    with open(out_file, 'w') as f:
        f.write("\n".join(p for p in tei_paragraphs(in_file)))


def replace_paragraphs(tei, out_file):
    tree = etree.parse(tei)
    text = tree.getroot().find(".//text")
    body = text.find(".//body")
    body.getparent().remove(body)
    newbody = etree.SubElement(text, "body")
    for p in tei_paragraphs(tei):
        par = etree.SubElement(newbody, "p")
        par.text = p
    res = etree.tounicode(tree, pretty_print=True)
    with open(out_file, 'w') as f:
        f.write(res)
    return res


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python tei_extracter.py {in_file} {out_file}")
        exit(1)
    replace_paragraphs(sys.argv[1], sys.argv[2])
