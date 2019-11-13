import pathlib
import re
import sys
import nl_core_news_sm
import tei_extracter as tei


def tei_tag(tag):
    return "{http://www.tei-c.org/ns/1.0}%s" % tag


def tei_path(tag):
    x = ".//{http://www.tei-c.org/ns/1.0}%s" % tag
    return x


def join_lines(content):
    res = ''
    line, *rest = content
    while rest:
        res += merge_lb(line)
        line, *rest = rest
    res += line
    return res


def text_content(element, tokenize):
    content = [text_and_tail(t) for t in element.iter() if t.tag != tei_tag('note') and t.getparent().tag != tei_tag('note')]
    return tokenize(join_lines(content)) + '\n\n'


def text_and_tail(elt):
    all_text = ''
    if elt.text:
        all_text += re.sub(r"\s+", " ", elt.text)
    if elt.tail:
        all_text += re.sub(r"\s+", " ", elt.tail)
    return all_text.strip()


def merge_lb(all_text):
    if all_text.endswith(' -'):
        return all_text[:-2]
    elif all_text.endswith('-'):
        return all_text[:-1]
    else:
        return all_text + ' '


def note_paragraph(element, tokenize):
    all_text = ''
    for t in element.iter():
        if t.tag == tei_tag('lb'):
            all_text = merge_lb(all_text)

        all_text += text_and_tail(t)
    return tokenize(all_text) + '\n'


def text_content_note(element, tokenize):
    paragraphs = element.findall(tei_path('p'))
    if paragraphs:
        return '\n'.join([note_paragraph(p, tokenize) for p in paragraphs]) + '\n'
    else:
        return note_paragraph(element, tokenize) + '\n'


def extract_pages(infile, tokenizer):
    pages = []

    text_tree = tei.parse(infile).getroot()
    docid = text_tree.find(tei_path('idno')).text
    bd = text_tree.find(tei_path('body'))
    page_str = ''
    current_page = 1
    for element in bd.iter(tei_tag('pb'), tei_tag('head'), tei_tag('p'), tei_tag('note')):
        if element.tag == tei_tag('head'):
            page_str += element.text + '\n\n'
        elif element.tag == tei_tag('p') and not element.getparent().tag == tei_tag('note'):
            page_str += text_content(element, tokenizer)
            if element.find(tei_path('pb')):
                pages.append((current_page, page_str.strip()))
                current_page = element.findall(tei_path('pb'))[-1].attrib['n']
                page_str = ''
        elif element.tag == tei_tag('pb'):
            pages.append((current_page, page_str.strip()))
            page_str = ''
            current_page = element.attrib['n']
        elif element.tag == tei_tag('note'):
            page_str += text_content_note(element, tokenizer)

    if page_str:
        pages.append((current_page, page_str.strip()))

    return docid, pages


def write(docid, pages, outdir):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    for p, content in pages:
        with open("{}/{}_{}.txt".format(outdir, docid, p), 'w') as f:
            f.write(content)


def tokenizer(model):
    def apply(text):
        return " ".join(token.text for token in model(text))
    if model is not None:
        return apply
    else:
        return lambda x: x


def process(infile, outdir):
    model = nl_core_news_sm.load()
    docid, pages = extract_pages(infile, tokenizer(None))   # replace by model to tokenize
    write(docid, pages, outdir)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("python vandam_extracter.py {infile} {outdir}")
        exit(1)
    process(sys.argv[1], sys.argv[2])
