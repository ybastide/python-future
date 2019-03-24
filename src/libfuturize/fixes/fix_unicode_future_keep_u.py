"""Fixer that changes unicode to text_type and unichr to chr, but -- unlike the
lib2to3 fix_unicode.py fixer, does not change u"..." into "...".

The reason is that Py3.3+ supports the u"..." string prefix, and, if
present, the prefix may provide useful information for disambiguating
between byte strings and unicode strings, which is often the hardest part
of the porting task.

"""
from lib2to3.fixer_util import touch_import
from lib2to3.pgen2 import token
from lib2to3 import fixer_base

_mapping = {u"unichr": u"chr", u"unicode": u"text_type"}


class FixUnicodeFutureKeepU(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "'unicode' | 'unichr'"

    def transform(self, node, results):
        if node.type == token.NAME:
            new = node.clone()
            new.value = _mapping[node.value]
            if node.value == u"unicode":
                touch_import(u"future.utils", u"text_type", node)
            return new
