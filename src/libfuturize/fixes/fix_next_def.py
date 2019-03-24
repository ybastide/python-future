"""
Based on fix_next.py by Collin Winter.

Fix next -> __next__ and define next() too.
"""
from lib2to3.pytree import Node, Leaf

from typing import TYPE_CHECKING
from lib2to3 import fixer_base
from lib2to3.fixer_util import find_binding, Name, Call, Assign, Newline

if TYPE_CHECKING:
    from typing import Any, Dict, Optional  # NOQA


bind_warning = "Calls to builtin next() possibly shadowed by global binding"


class FixNextDef(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
    classdef< 'class' any+ ':'
              suite< any*
                     next=funcdef< 'def'
                              name='next'
                              parameters< '(' NAME ')' > any+ >
                     any* > >
    """

    order = "pre"  # Pre-order tree traversal

    def start_tree(self, tree, filename):
        super(FixNextDef, self).start_tree(tree, filename)

        n = find_binding(u"next", tree)
        if n:
            self.warning(n, bind_warning)
            self.shadowed_next = True
        else:
            self.shadowed_next = False

    def transform(self, node, results):
        # type: (Node, Dict[str, Any]) -> None
        assert results

        name = results["name"]  # type: Leaf
        next_node = results["next"]  # type: Node

        n = Name(u"__next__", prefix=name.prefix)
        name.replace(n)
        child = Assign(Name(u"next", prefix=name.prefix), Name(u"__next__"))
        child.children[0].column = name.column
        # idx, ch = None, None  # type: Optional[int], Optional[Node]
        # for ch in node.children:
        #     if isinstance(ch, Node):
        #         try:
        #             idx = ch.children.index(name)
        #             break
        #         except ValueError:
        #             pass
        # if idx is not None:
        #     ch.insert_child(idx + 1, Newline())
        #     ch.insert_child(idx + 2, child)
        #     ch.insert_child(idx + 3, Newline())
        idx = next_node.parent.children.index(next_node.next_sibling)
        next_node.parent.insert_child(idx, Newline())
        next_node.parent.insert_child(idx + 1, child)
        next_node.parent.insert_child(idx + 2, Newline())
