from utils.tei_tree import TextTree, NEXT_PAGE_FLAG, PREVIOUS_PAGE_FLAG
from utils.tei_xml import body

IN_FILE = 'data/tests/vandam_extract.xml'


def test_tei_clean():
    tree = TextTree.make(body(IN_FILE))
    tree.remove_multiple_whitespace()
    assert not tree.text
    assert not tree.tail


def test_reshape():
    tree = TextTree.make(body(IN_FILE))
    node = tree.children[1].children[1].children[4]
    assert node.tag == 'p'
    assert node.text.startswith('Inmiddels is de Camer van Delft')
    assert len(node.children) == 6
    assert node.children[5].tag == 'pb'
    assert node.children[5].tail.startswith(' Compagnie')
    reshaped_children = node.resolve_page_breaks()
    assert len(reshaped_children) == 7
    assert reshaped_children[2].tail.endswith(NEXT_PAGE_FLAG)
    assert not reshaped_children[5].tail
    assert reshaped_children[6].tag == 'p'
    assert reshaped_children[6].text.startswith('{} Compagnie'.format(PREVIOUS_PAGE_FLAG))
