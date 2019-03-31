"""
Fix patterns like

    filter(func, iter)[i]
"""
from lib2to3 import fixer_base
from lib2to3.fixer_util import Name, LParen, RParen
from lib2to3.pytree import Node, Leaf

replaced_builtin_fns = """filter map zip""".split()
expression = "|".join(["name='{0}'".format(name) for name in replaced_builtin_fns])


class FixIndexOnIterator(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """
              power<
                 ({expression}) fn_trailer=trailer< '(' [any] ')' > getitem=trailer< '[' any ']' >
              rest=any* >
              |
              power<
                 ({expression}) fn_trailer=trailer< '(' [any] ')' > 
                 method_call=trailer< '.' method=any > method_args=trailer< '(' [any] ')' >
              rest=any* >
    """.format(expression=expression)

    def transform(self, node, results):
        if "getitem" in results:
            return self.transform_array_access(node, results)
        return self.transform_method_call(node, results)

    def transform_array_access(self, node, results):
        name = results["name"]  # type: Leaf
        fn_trailer = results["fn_trailer"]  # type: Node
        getitem = results["getitem"]  # type: Node
        rest = results["rest"]
        new_node = Node(self.syms.power, [
            Name(u"list"),
            Node(self.syms.trailer, [
                LParen(),
                Name(name.value),
                fn_trailer.clone(),
                RParen(),
                getitem.clone(),
            ] + [r.clone() for r in rest])
        ],
                        prefix=node.prefix)
        return new_node

    def transform_method_call(self, node, results):
        name = results["name"]  # type: Leaf
        fn_trailer = results["fn_trailer"]  # type: Node
        method_call = results["method_call"]
        method_args = results["method_args"]
        rest = results["rest"]
        new_node = Node(self.syms.power, [
            Name(u"list"),
            Node(self.syms.trailer, [
                LParen(),
                Name(name.value),
                fn_trailer.clone(),
                RParen(),
                method_call.clone(),
                method_args.clone(),
            ] + [r.clone() for r in rest])
        ],
                        prefix=node.prefix)
        return new_node
