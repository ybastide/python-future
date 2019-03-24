"""Replace isinstance(c, basestring) with isinstance(v, text_types).
"""

from lib2to3 import fixer_base
from lib2to3.fixer_util import touch_import

VALUE = u"string_types"


class FixBasestringTextTypes(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
              power<
                 'isinstance' trailer< '(' arglist< var=any ',' type='basestring' > ')' >
              tail=any* >
              |
              power<
                 'isinstance' trailer< '(' arglist< var=any ',' type=atom< '(' testlist_gexp< 'str' ',' 'unicode' > ')' > > ')' >
              tail=any* >
              |
              power<
                 'isinstance' trailer< '(' arglist< var=any ',' type=atom< '(' testlist_gexp< 'unicode' ',' 'str' > ')' > > ')' >
              tail=any* >
              """

    def transform(self, node, results):
        touch_import(u"future.utils", VALUE, node)
        node = results["type"]
        node.value = VALUE
        node.changed()
