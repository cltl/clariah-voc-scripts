"""Text extraction from TEI files"""
import re
from utils.func import flatmap

import utils.tei_xml as tx

NEXT_PAGE_FLAG = "<PB>"
PREVIOUS_PAGE_FLAG = "</PB>"


class TextTree:
    """Represents a TEI xml tree and allows for text extraction.

    Textual content is modified by:
    - joining line breaks;
    - removing multiple whitespace.
    Page structure is preserved:
    - trailing paragraphs are extracted as separate paragraphs;
    - PageBreak symbols mark interrupted paragraphs across page breaks.
    Page collection returns a list of tuples of page number and paragraphs
    """

    def __init__(self, tag, text, tail, attrib, children):
        self.tag = tag
        self.text = text
        self.tail = tail
        self.attrib = attrib
        self.children = children

    def __str__(self):
        return self.indented_str("")

    @classmethod
    def make(cls, elt):
        text = ''
        tail = ''
        if elt.text is not None:
            text = elt.text
        if elt.tail is not None:
            tail = elt.tail
        return cls(tx.untag(elt.tag), text, tail, elt.attrib, [cls.make(child) for child in elt])

    @classmethod
    def make_paragraph(cls, text, tail):
        return cls(tx.P, text, tail, None, [])

    @staticmethod
    def clean_line_break(text):
        if text.endswith(' -'):
            return text[:-2]
        elif text.endswith('-'):
            return text[:-1]
        elif text == PREVIOUS_PAGE_FLAG:
            return text
        else:
            return text + ' '

    def indented_str(self, indent):
        result = "{}({}) [{}] [{}]\n".format(indent, self.tag, self.text, self.tail)
        result += "\n".join([child.indented_str(indent + "  ") for child in self.children])
        return result

    def resolve_page_breaks(self):
        """Levels up page breaks and notes in paragraphs across pages.

        If a paragraph contains a page-break, splits the paragraph at the page breaks.
        The paragraph is then replaced by a list of nodes containing the paragraph up to the notes and page breaks,
        followed by the latter.
        """
        def promote(n):
            return tx.is_page_break(n) or tx.is_note(n)

        def contains_paragraph_tail(n):
            return n.tail

        def with_flag(n, cs):
            if cs:
                cs[-1].tail += NEXT_PAGE_FLAG
                n.children = cs
            else:
                n.tail += NEXT_PAGE_FLAG
            return n

        if tx.is_paragraph(self) and any(tx.is_page_break(c) for c in self.children):
            replacement_nodes = []
            children = []
            node = self.make_paragraph(self.text, self.tail)
            for c in self.children:
                if promote(c):
                    if node is not None:
                        replacement_nodes.append(with_flag(node, children))
                        node = None
                        children = []
                    if contains_paragraph_tail(c):
                        replacement_nodes.append(TextTree(c.tag, c.text, '', c.attrib, c.children))
                        node = self.make_paragraph(PREVIOUS_PAGE_FLAG + c.tail, '')
                    else:
                        replacement_nodes.append(c)
                else:
                    children.append(c)

            if node is not None:
                node.children = children
                replacement_nodes.append(node)
            return replacement_nodes
        else:
            return [self]

    def remove_multiple_whitespace(self):
        if self.text:
            self.text = re.sub(r"\s\s+", ' ', self.text)
        if not self.text or re.match(r"^\s$", self.text):
            self.text = ''
        if self.tail:
            self.tail = re.sub(r"\s\s+", ' ', self.tail)
        if not self.tail or re.match(r"^\s$", self.tail):
            self.tail = ''
        for child in self.children:
            child.remove_multiple_whitespace()

    def subsumed_text(self):
        text = self.text
        for c in self.children:
            if tx.is_line_break(c):
                text = self.clean_line_break(text)
            text += c.subsumed_text()
        text += self.tail
        return text

    def reshape(self):
        """Visits the tree, splitting interrupted paragraph nodes."""
        self.children = flatmap(lambda x: x.resolve_page_breaks(), self.children)
        for c in self.children:
            c.reshape()

    def collect_loop(self, pages, page, paragraphs):
        if tx.is_head(self) or tx.is_note(self) or tx.is_paragraph(self):
            paragraphs.append(self.subsumed_text())
        elif tx.is_page_break(self):
            if paragraphs:
                pages.append((page, paragraphs))
            page = self.attrib['n']
            paragraphs = []
        else:
            for c in self.children:
                pages, page, paragraphs = c.collect_loop(pages, page, paragraphs)
        return pages, page, paragraphs

    def collect_pages(self):
        self.remove_multiple_whitespace()
        self.reshape()
        pages, page, paragraphs = self.collect_loop([], 0, [])
        if paragraphs:
            pages.append((page, paragraphs))
        return pages

