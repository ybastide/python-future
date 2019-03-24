"""
Fix patterns like

    filter(func, iter)[i]
"""
from lib2to3 import fixer_base


class FixIndexOnIterator(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """
              power<
              >
    """
