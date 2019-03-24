"""
Fix patterns like

    filter(func, iter)[i]
    filter(func, iter).index(x)
"""
from lib2to3 import fixer_base

replaced_builtin_fns = """filter map zip""".split()
expression = "|".join(["name='{0}'".format(name) for name in replaced_builtin_fns])


class FixIndexOnIterator(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """
              power<
                 ({expression}) trailer< '(' [arglist=any] ')' > getitem=atom< '[' (index=any) ']' >
              rest=any* >
              |
              power<
                 ({expression}) trailer< '(' [arglist=any] ')' > '.'
              rest=any* >
    """.format(expression=expression)

    def transform(self, node, results):
        if "getitem" in results:
            return self.transform_array_access(node, results)
        return self.transform_method_call(node, results)

    def transform_array_access(self, node, results):
        pass

    def transform_method_call(self, node, results):
        pass
