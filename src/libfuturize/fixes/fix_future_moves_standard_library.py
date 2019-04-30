"""
Copy-pasted from lib2to3/fixes/fix_imports.py

Changes any imports needed to reflect the standard library reorganization
using futures.move.
"""
from lib2to3 import fixer_base
from lib2to3.fixer_util import attr_chain, Name

from future.utils import text_type

MAPPING = {
    "StringIO": "io",
    "cStringIO": "io",
    "cPickle": "future.moves.pickle",
    "__builtin__": "builtins",
    "copy_reg": "future.moves.copyreg",
    "Queue": "future.moves.queue",
    "SocketServer": "future.moves.socketserver",
    "ConfigParser": "future.moves.configparser",
    "repr": "future.moves.reprlib",
    "FileDialog": "future.moves.tkinter.filedialog",
    "tkFileDialog": "future.moves.tkinter.filedialog",
    "SimpleDialog": "future.moves.tkinter.simpledialog",
    "tkSimpleDialog": "future.moves.tkinter.simpledialog",
    "tkColorChooser": "future.moves.tkinter.colorchooser",
    "tkCommonDialog": "future.moves.tkinter.commondialog",
    "Dialog": "future.moves.tkinter.dialog",
    "Tkdnd": "future.moves.tkinter.dnd",
    "tkFont": "future.moves.tkinter.font",
    "tkMessageBox": "future.moves.tkinter.messagebox",
    "ScrolledText": "future.moves.tkinter.scrolledtext",
    "Tkconstants": "future.moves.tkinter.constants",
    "Tix": "future.moves.tkinter.tix",
    "ttk": "future.moves.tkinter.ttk",
    "Tkinter": "future.moves.tkinter",
    "markupbase": "future.moves._markupbase",
    "_winreg": "future.moves.winreg",
    "thread": "future.moves._thread",
    "dummy_thread": "future.moves._dummy_thread",
    # anydbm and whichdb are handled by fix_imports2
    "dbhash": "future.moves.dbm.bsd",
    "dumbdbm": "future.moves.dbm.dumb",
    "dbm": "future.moves.dbm.ndbm",
    "gdbm": "future.moves.dbm.gnu",
    "xmlrpclib": "future.moves.xmlrpc.client",
    "DocXMLRPCServer": "future.moves.xmlrpc.server",
    "SimpleXMLRPCServer": "future.moves.xmlrpc.server",
    "httplib": "future.moves.http.client",
    "htmlentitydefs": "future.moves.html.entities",
    "HTMLParser": "future.moves.html.parser",
    "Cookie": "future.moves.http.cookies",
    "cookielib": "future.moves.http.cookiejar",
    "BaseHTTPServer": "future.moves.http.server",
    "SimpleHTTPServer": "future.moves.http.server",
    "CGIHTTPServer": "future.moves.http.server",
    # 'test.test_support': 'test.support',
    "commands": "future.moves.subprocess",
    "UserString": "future.moves.collections",
    "UserList": "future.moves.collections",
    "urlparse": "future.moves.urllib.parse",
    "robotparser": "future.moves.urllib.robotparser",
}


def alternates(members):
    return "(" + "|".join(map(repr, members)) + ")"


def build_pattern(mapping=MAPPING):
    mod_list = " | ".join(["module_name='%s'" % key for key in mapping])
    bare_names = alternates(mapping.keys())

    yield """name_import=import_name< 'import' ((%s) |
               multiple_imports=dotted_as_names< any* (%s) any* >) >
          """ % (
        mod_list,
        mod_list,
    )
    yield """import_from< 'from' (%s) 'import' ['(']
              ( any | import_as_name< any 'as' any > |
                import_as_names< any* >)  [')'] >
          """ % mod_list
    yield """import_name< 'import' (dotted_as_name< (%s) 'as' any > |
               multiple_imports=dotted_as_names<
                 any* dotted_as_name< (%s) 'as' any > any* >) >
          """ % (
        mod_list,
        mod_list,
    )

    # Find usages of module members in code e.g. thread.foo(bar)
    yield "power< bare_with_attr=(%s) trailer<'.' any > any* >" % bare_names


class FixFutureMovesStandardLibrary(fixer_base.BaseFix):

    BM_compatible = True
    keep_line_order = True
    # This is overridden in fix_imports2.
    mapping = MAPPING

    # We want to run this fixer late, so fix_import doesn't try to make stdlib
    # renames into relative imports.
    run_order = 6

    def build_pattern(self):
        return "|".join(build_pattern(self.mapping))

    def compile_pattern(self):
        # We override this, so MAPPING can be pragmatically altered and the
        # changes will be reflected in PATTERN.
        self.PATTERN = self.build_pattern()
        super(FixFutureMovesStandardLibrary, self).compile_pattern()

    # Don't match the node if it's within another match.
    def match(self, node):
        match = super(FixFutureMovesStandardLibrary, self).match
        results = match(node)
        if results:
            # Module usage could be in the trailer of an attribute lookup, so we
            # might have nested matches when "bare_with_attr" is present.
            if "bare_with_attr" not in results and any(
                match(obj) for obj in attr_chain(node, "parent")
            ):
                return False
            return results
        return False

    def start_tree(self, tree, filename):
        super(FixFutureMovesStandardLibrary, self).start_tree(tree, filename)
        self.replace = {}

    def transform(self, node, results):
        import_mod = results.get("module_name")
        if import_mod:
            mod_name = import_mod.value
            new_name = self.mapping[mod_name]
            import_mod.replace(Name(new_name, prefix=import_mod.prefix))
            if "name_import" in results:
                # If it's not a "from x import x, y" or "import x as y" import,
                # marked its usage to be replaced.
                self.replace[mod_name] = text_type(new_name)
            if "multiple_imports" in results:
                # This is a nasty hack to fix multiple imports on a line (e.g.,
                # "import StringIO, urlparse"). The problem is that I can't
                # figure out an easy way to make a pattern recognize the keys of
                # MAPPING randomly sprinkled in an import statement.
                results = self.match(node)
                if results:
                    self.transform(node, results)
        else:
            # Replace usage of the module.
            bare_name = results["bare_with_attr"][0]
            new_name = self.replace.get(bare_name.value)
            if new_name:
                bare_name.replace(Name(new_name, prefix=bare_name.prefix))
