"""
Based on fix_next.py by Collin Winter.

Fix next -> __next__, keeping next as an alias.
"""
import token
from lib2to3 import fixer_base
from lib2to3.fixer_util import Name, Newline, find_binding, find_indentation, syms
from lib2to3.pytree import Leaf, Node

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict, Union  # NOQA


bind_warning = "Calls to builtin next() possibly shadowed by global binding"


class FixNextDef(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
    classdef< 'class' any+ ':'
              suite=suite< any*
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
        next_ = results["next"]  # type: Node
        suite = results["suite"]  # type: Node
        next_sibling = next_.next_sibling  # type: Union[Leaf, Node]

        n = Name(u"__next__", prefix=name.prefix)
        name.replace(n)
        indentation = find_indentation(next_)
        _ = suite == next_.parent
        child = Node(
            syms.simple_stmt,
            [
                Node(
                    syms.expr_stmt,
                    [
                        Name(u"next"),
                        Leaf(token.EQUAL, u"=", prefix=u" "),
                        Name(u"__next__", prefix=u" "),
                    ],
                ),
                Newline(),
            ],
        )
        idx = suite.children.index(next_)
        suite.insert_child(idx + 1, child)
        if next_sibling and next_sibling.prefix == u"":
            next_sibling.prefix = u"\n" + indentation
        _ = 1  # debug
