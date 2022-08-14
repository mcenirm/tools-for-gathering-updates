from __future__ import annotations

from collections.abc import Mapping
from typing import Generator, Iterator
from xml.etree.ElementTree import Element, ElementTree


class ElementTreeParentMap(Mapping[Element, Element]):
    """

    >>> tree, pmap = _mtp("<a><b><c1/><c2/></b></a>")
    >>> root = tree.getroot()
    >>> b = root.find("b")
    >>> c1 = b.find("c1")
    >>> pmap[root] is None
    True
    >>> pmap[b] == root
    True
    >>> pmap[c1] == b
    True
    >>> tuple(map(len, map(set, (pmap, pmap.keys(), pmap.values()))))
    (4, 4, 3)
    """

    def __init__(self, tree: ElementTree) -> None:
        self._tree = tree
        self._map = dict()
        self._map[tree.getroot()] = None
        for p in tree.iter():
            for c in p:
                self._map[c] = p

    def __getitem__(self, key: Element) -> Element:
        return self._map[key]

    def __iter__(self) -> Iterator[Element]:
        return iter(self._map)

    def __len__(self) -> int:
        return len(self._map)

    def ancestors(self, e: Element) -> Generator[Element, None, None]:
        """

        >>> tree, pmap = _mtp("<a><b><c1/><c2/></b></a>")
        >>> c2 = tree.getroot()[0][1]
        >>> c2.tag
        'c2'
        >>> for p in pmap.ancestors(c2):
        ...     p.tag
        'b'
        'a'
        """
        p = e
        while (p := self[p]) is not None:
            yield p


def short_tag(tag: str) -> str:
    """

    >>> short_tag("foo")
    'foo'
    >>> short_tag("{foo}bar")
    'bar'
    """
    return tag.split("}")[-1]


def _mtp(x: str) -> tuple[ElementTree, ElementTreeParentMap]:
    from io import StringIO
    from xml.etree.ElementTree import parse

    f = StringIO(x)
    tree = parse(f)
    pmap = ElementTreeParentMap(tree)
    return tree, pmap


if __name__ == "__main__":
    from doctest import FAIL_FAST, testmod

    testmod(optionflags=FAIL_FAST)
