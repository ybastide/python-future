"""Fixer for dict methods using future.utils.
Based on lib2to3/fixes/fix_dict.py

d.keys() -> list(d.keys())
d.items() -> list(d.items())
d.values() -> list(d.values())

d.iterkeys() -> iterkeys(d)
d.iteritems() -> iteritems(d)
d.itervalues() -> itervalues(d)

d.viewkeys() -> viewkeys(d)
d.viewitems() -> viewitems(d)
d.viewvalues() -> viewvalues(d)

for x in d.keys() -> for x in d.iterkeys() (/values/items)
"""
from lib2to3 import fixer_base, pytree, fixer_util, patcomp
from lib2to3.fixer_util import Name, Call, Dot, touch_import
from lib2to3.fixes.fix_dict import iter_exempt


class FixFutureDict(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """
    power< head=any+
         trailer< '.' method=('keys'|'items'|'values'|
                              'iterkeys'|'iteritems'|'itervalues'|
                              'viewkeys'|'viewitems'|'viewvalues') >
         parens=trailer< '(' ')' >
         tail=any*
    >
    """

    def transform(self, node, results):
        head = results["head"]
        method = results["method"][0]  # Extract node for method name
        tail = results["tail"]
        syms = self.syms
        method_name = method.value
        isiter = method_name.startswith(u"iter")
        isview = method_name.startswith(u"view")
        if isiter or isview:
            base_method_name = method_name[4:]
        else:
            base_method_name = method_name
        assert base_method_name in (u"keys", u"items", u"values"), repr(method)
        head = [n.clone() for n in head]
        tail = [n.clone() for n in tail]
        special = not tail and self.in_special_context(node, isiter)
        loop = self.in_for_loop(node, isiter, isview)
        if loop:
            method_name = "iter" + base_method_name
            isiter = True
        if not (isiter or isview):
            args = head + [
                pytree.Node(
                    syms.trailer, [Dot(), Name(base_method_name, prefix=method.prefix)]
                ),
                results["parens"].clone(),
            ]
        else:
            args = head
            touch_import("future.utils", method_name, node)
        new = pytree.Node(syms.power, args)
        if not special:
            new.prefix = u""
            new = Call(Name(method_name if isiter or isview else u"list"), [new])
        if tail:
            new = pytree.Node(syms.power, [new] + tail)
        new.prefix = node.prefix
        return new

    P1 = "power< func=NAME trailer< '(' node=any ')' > any* >"
    p1 = patcomp.compile_pattern(P1)

    def in_special_context(self, node, isiter):
        if node.parent is None:
            return False
        results = {}
        if (
            node.parent.parent is not None
            and self.p1.match(node.parent.parent, results)
            and results["node"] is node
        ):
            if isiter:
                # iter(d.iterkeys()) -> iter(d.keys()), etc.
                return results["func"].value in iter_exempt
            else:
                # list(d.keys()) -> list(d.keys()), etc.
                return results["func"].value in fixer_util.consuming_calls
        return False

    P2 = """for_stmt< 'for' any 'in' node=any ':' any* >
            | comp_for< 'for' any 'in' node=any any* >
         """
    p2 = patcomp.compile_pattern(P2)

    def in_for_loop(self, node, isiter, isview):
        if node.parent is None:
            return False
        if isiter or isview:  # already OK
            return False
        results = {}
        return self.p2.match(node.parent, results) and results["node"] is node
