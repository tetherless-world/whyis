"""An experimental XPath-based streaming filter for ElementTree's iterparse

For details see:
http://dalkescientific.com/writings/diary/archive/2006/11/06/iterparse_filter.html
"""
from __future__ import print_function
# I have got to rearrange my site to use shorter URLs.

from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import object
__version__ = "0.9-experimental"

import re

dtd_validation = False
try:
  from lxml import etree
  dtd_validation = True
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
      except ImportError:
          # normal ElementTree install
          import elementtree.ElementTree as etree

# define "letter" as "any character except /:[]()@={}* or in \s"
#   (XXX make it match the XML spec)
# A URI is:
#   letter+
#   letter+ ':' letter+   --- a namespace prefixed term, like xml:space
#   '{'  [^}]*  '}' letter+  --- a Clark namespace term, like {http://a}b
# Can also use a '*' in place of a URI or in the tag part of a namespaced field
#
# URIs are separated only be '/' and '//'.
# These may not occur together, eg, '///' is not allowed.

# Basing this tokenization method in part on elementtree.ElementPath
xpath_tokenizer = re.compile( r"""
(// | / )  # separators

| (?:  # namespaced term
  ([^\/\:\[\]\(\)\@\=\{\}\*\s]+) :    # namespace
  ([^\/\:\[\]\(\)\@\=\{\}\*\s]+|\*)      # tag
) 

| (?:
  \{([^}]*)\}      # namespace in Clark notation
  ([^\/\:\[\]\(\)\@\=\{\}\*\s]+|\*)      # tag  
)

| ([^\/\:\[\]\(\)\@\=\{\}\*\s]+|\*)      # tag with no namespace

| (.)             # everything else; used to identify errors
""", re.X).findall
# """""  # fix emacs cruft; having too many special characters fools it
    

def tokenize(s):
    pos = 0
    for token in xpath_tokenizer(s):
        op = token[0]
        if op in ("/", "//"):
            yield (op, None, pos)
        elif token[1]:
            yield ("namespace", (token[1], token[2]), pos)
        elif token[3]:
            yield ("clark", (token[3], token[4]), pos)
        elif token[5]:
            yield ("default", token[5], pos)
        elif token[6]:
            raise SyntaxError("Unknown symbol %r at position %d" %
                              (token[6], pos))
        else:
            raise AssertionError("Unknown token: %r" % (token,))

def _make_original_tag(op, args):
    if op == "namespace":
        return "%s:%s" % (args[0], args[1])
    if op == "clark":
        return "{%s}:%s" % (args[0], args[1])
    if op == "default":
        return args
    raise AssertionError("Strange: %r %r" % (op, args))

def _verify_ordering(tokens):
    if not tokens:
        raise SyntaxError(
            "empty xpath not supported (don't know how to handle that case)")
    pos = 0
    prev = None
    SEP = 1
    URI = 2
    # Check that the path alternates between separator and uri
    for op, args, pos in tokens:
        if op in ("/", "//"):
            if prev == SEP:
                raise SyntaxError(
                   "separator %r may not follow separator at position %d" %
                   (op, pos))
            prev = SEP
        elif op in ("namespace", "clark", "default"):
            if prev == URI:
                errmsg = _make_original_tag(op, args)
                raise SyntaxError(
                   "%r may not follow a separator at position %d" %
                   (errormsg, pos))
            prev = URI
        else:
            raise AssertionError("Unknown op: %r, %r, %r" % (op, args, pos))

    if tokens[-1][0] == "//":
        raise AssertionError("xpath may not end with '//'")

# There are further optimizations.  For example, if this
# returned a match function instead of the regex then it
# could special case terms like /blah//* to mean "startswith('/blah/')"
#   The small performance advantages for most cases doesn't
# currently warrant the extra work.
def to_regexp(s, namespaces={}, default_namespace=None):
    tokens = list(tokenize(s))
    _verify_ordering(tokens)
    
    ### Process the tokens
    re_terms = []
    if tokens[0][0] == "/":
        re_terms.append("^")
        tokens.pop(0)

    for op, args, pos in tokens:
        if op == "/":
            pass
        elif op == "//":
            re_terms.append("(/[^/]+)*")
        elif op in ("namespace", "clark", "default"):
            # Break each apart to get the correct namespace and tag
            if op == "namespace":
                namespace, tag = args
                try:
                    full_namespace = namespaces[namespace]
                except KeyError:
                    raise SyntaxError("Unknown namespace %r at position %d" %
                                      (namespace, pos))
            elif op == "clark":
                full_namespace, tag = args
            elif op == "default":
                full_namespace = default_namespace
                tag = args

            # Figure out which pattern to use for the combination
            # of (namespace, namespace==None) x (tag, tag=='*')
            if full_namespace is None:
                # No namespace specified
                if tag == "*":
                    # Select everything between the /s
                    re_terms.append("/[^/]+")
                else:
                    # Select exactly the tag, no namespace
                    re_terms.append("/%s" % (re.escape(tag),))
            else:
                # namespace specified
                if tag == "*":
                    # Select only fields in the given namespace
                    re_terms.append("/" +
                                    re.escape("{%s}" % (full_namespace,)) +
                                    "[^/]+")
                else:
                    # Must match namespace and tag, exactly
                    re_terms.append("/" +
                                    re.escape("{%s}%s" % (full_namespace, tag)))
        else:
            raise AssertionError("Unknown op %r" % (op,))

    # Must be a complete match
    re_terms.append("/$")
    
    return "".join(re_terms)

class IterParseFilter(object):
    def __init__(self, namespaces=None, default_namespace=None, validate_dtd=False):
        if namespaces is None:
            namespaces = {}
        self.namespaces = namespaces
        self.default_namespace = default_namespace
        self.validate_dtd = validate_dtd

        self._start_document_handlers = []
        self._end_document_handlers = []
        
        self._start_filters = []
        self._end_filters = []
        self._default_start_filters = []
        self._default_end_filters = []
        self._iter_start_filters = []
        self._iter_end_filters = []

        self._start_ns_handlers = []
        self._end_ns_handlers = []
        self._iter_start_ns = False
        self._iter_end_ns = False

    def on_start_document(self, handler):
        self._start_document_handlers.append(handler)
    def on_end_document(self, handler):
        self._end_document_handlers.append(handler)
        
    def _add_handler(self, filters, path, handler):
        path_re = to_regexp(path,
                            namespaces = self.namespaces,
                            default_namespace = self.default_namespace)
        filters.append( (path, re.compile(path_re).search, handler) )
    def on_start(self, path, handler):
        self._add_handler(self._start_filters, path, handler)
    def on_end(self, path, handler):
        self._add_handler(self._end_filters, path, handler)
    def on_start_default(self, path, handler):
        self._add_handler(self._default_start_filters, path, handler)
    def on_end_default(self, path, handler):
        self._add_handler(self._default_end_filters, path, handler)

    def _add_yielder(self, yielders, path):
        path_re = to_regexp(path,
                            namespaces = self.namespaces,
                            default_namespace = self.default_namespace)
                            
        yielders.append( (path, re.compile(path_re).search) )
    def iter_start(self, path):
        self._add_yielder(self._iter_start_filters, path)
    def iter_end(self, path):
        self._add_yielder(self._iter_end_filters, path)

    def on_start_ns(self, handler):
        self._start_ns_handlers.append(handler)
    def on_end_ns(self, handler):
        self._end_ns_handlers.append(handler)
    def iter_start_ns(self):
        self._iter_start_ns = True
    def iter_end_ns(self):
        self._iter_end_ns = True

    def _get_filter_info(self, category):
        for (_, _, pat, handler) in self.filters[category]:
            yield (pat, handler)

    def create_fa(self):
        # Make copies of everything to emphasize that they must
        # not be changed during processing.
        return FilterAutomata(
            start_document_handlers = self._start_document_handlers,
            end_document_handlers = self._end_document_handlers[::-1], # reverse!
            start_filters = self._start_filters[:],
            end_filters = self._end_filters[::-1],  # reversing here!
            default_start_filters = self._default_start_filters[:],
            default_end_filters = self._default_end_filters[::-1], # reversing!
            iter_start_filters = self._iter_start_filters[:],
            iter_end_filters = self._iter_end_filters[:],

            start_ns_handlers = self._start_ns_handlers[:],
            end_ns_handlers = self._end_ns_handlers[::-1],  # reversing here!
            iter_start_ns = self._iter_start_ns,
            iter_end_ns = self._iter_end_ns)

    # These forward to the underlying automata; make a new one each time.
    def parse(self, file, state=None):
        return self.create_fa().parse(file, state, self.validate_dtd)

    # Experimental
    def iterparse(self, file):
        return self.create_fa().iterparse(file, self.validate_dtd)
    # I need a better name
    def handler_parse(self, file, state=None):
        return self.create_fa().handler_parse(file, state)
            

class FilterAutomata(object):
    def __init__(self,
                 start_document_handlers,
                 end_document_handlers,
                 
                 start_filters,
                 end_filters,
                 default_start_filters,
                 default_end_filters,
                 iter_start_filters,
                 iter_end_filters,

                 start_ns_handlers,
                 end_ns_handlers,
                 iter_start_ns,
                 iter_end_ns):
        self.start_document_handlers = start_document_handlers
        self.end_document_handlers = end_document_handlers
        
        self.start_filters = start_filters
        self.end_filters = end_filters
        self.default_start_filters = default_start_filters
        self.default_end_filters = default_end_filters
        self.iter_start_filters = iter_start_filters
        self.iter_end_filters = iter_end_filters
        
        self.start_ns_handlers =  start_ns_handlers
        self.end_ns_handlers = end_ns_handlers
        self.iter_start_ns = iter_start_ns
        self.iter_end_ns = iter_end_ns

        # Can cache results over multiple invocations
        # NOTE: not thread-safe.  Though given the GIL
        # this shouldn't be a problem.
        self.dfa = {}

    def _new_node(self, stack_as_path):
        start_handlers = []
        for (path, matcher, handler) in self.start_filters:
            if matcher(stack_as_path):
                start_handlers.append(handler)
                
        if not start_handlers:
            # Any defaults?
            for (path, matcher, handler) in self.default_start_filters:
                if matcher(stack_as_path):
                    start_handlers.append(handler)

        end_handlers = []
        for (path, matcher, handler) in self.end_filters:
            if matcher(stack_as_path):
                end_handlers.append(handler)
        if not end_handlers:
            # Any defaults?
            for (path, matcher, handler) in self.default_end_filters:
                if matcher(stack_as_path):
                    end_handlers.append(handler)
                            
        # Have all the handlers, now check for yields
        iter_start = False
        for (path, matcher) in self.iter_start_filters:
            if matcher(stack_as_path):
                iter_start = True
                break
            
        iter_end = False
        for (path, matcher) in self.iter_end_filters:
            if matcher(stack_as_path):
                iter_end = True
                break

        new_node = ({}, start_handlers, end_handlers, iter_start, iter_end)
        return new_node

    def _needed_actions(self, iter=False, handler=False):
        if (not handler) and (not cb):
            raise AssertionError("must specify one")
        actions = ("start", "end")
        if ( (handler and self.start_ns_handlers) or
             (iter and self.iter_start_ns) ):
            actions = actions + ("start-ns",)

        if ( (handler and self.end_ns_handlers) or
             (iter and self.iter_end_ns) ):
            actions = actions + ("end-ns",)
        return actions

    # I plan to implement 'handler_parse' as a near copy of 'parse'
    # but without any yield statements.
    def handler_parse(self, file, state=None):
        for x in self.parse(file, state):
            pass
        
    # I plan to implement 'iterparse' as a near copy of 'parse'
    # but without any references to callbacks
    def iterparse(self, file, validate_dtd=False):
        return self.parse(file, None, validate_dtd)

    def parse(self, file, state=None, validate_dtd=False):
        if not dtd_validation:
            validate_dtd = False
        node_stack = []
        node_stack_append = node_stack.append
        tag_stack = []
        tag_stack_append = tag_stack.append
        # children, start handlers, end handlers, iter start, iter end
        node = (self.dfa, [], [], False, False)

        # synthesize start-document events
        for handler in self.start_document_handlers:
            handler("start-document", None, state)

        # figure out if I also need start-ns and/or end-ns events
        needed_actions = self._needed_actions(True, True)
        kwargs = {}
        if validate_dtd:
            kwargs = dict(dtd_validation=True)
        last_start = 0
        total_mem = 0
        before = None
        for (event, ele) in etree.iterparse(file, needed_actions, **kwargs):
            if event == "start":
                tag = ele.tag
                # Descend into node; track where I am
                tag_stack_append(tag)
                node_stack_append(node)
                stack_as_path = "/" + ("/".join(tag_stack)) + "/"
                new_node = self._new_node(stack_as_path)
                node = new_node

                # call the start handlers then yield the element
                for start_handler in node[1]:
                    start_handler(event, ele, state)
                if node[3]:
                    yield (event, ele)
                #print total_mem

            elif event == "end":
                # call the end handlers then yield the element
                for end_handler in node[2]:
                    end_handler(event, ele, state)
                del tag_stack[-1]
                if node[4]:
                    yield (event, ele)
                    # It's safe to call clear() here because no descendants will be
                    # accessed
                    ele.clear()
                    if ele.getparent() is not None:
                        ele.getparent().remove(ele)

                    # Also eliminate now-empty references from the root node to elem
                    #for ancestor in ele.xpath('ancestor-or-self::*'):
                    #    while ancestor.getprevious() is not None:
                    #        del ancestor.getparent()[0]
                node = node_stack.pop()

            elif event == "start-ns":
                for handler in self.start_ns_handlers:
                    handler(event, ele, state)
                if self.iter_start_ns:
                    print('start-ns')
                    yield (event, ele)
                
            elif event == "end-ns":
                for handler in self.end_ns_handlers:
                    handler(event, ele, state)
                if self.iter_start_ns:
                    print('end-ns')
                    yield (event, ele)
                    # It's safe to call clear() here because no descendants will be
                    # accessed
                    ele.clear()
                    ele.getparent().remove(ele)
                    # Also eliminate now-empty references from the root node to elem
                    #for ancestor in ele.xpath('ancestor-or-self::*'):
                    #    while ancestor.getprevious() is not None:
                    #        del ancestor.getparent()[0]
                    
        for handler in self.end_document_handlers:
            handler("end-document", None, state)


#### An incomplete test suite ####

def test_path(path, args):
    #print "**** test_path", repr(path), repr(args)
    pattern = to_regexp(path)
    pat = re.compile(pattern)
    s = "/" + ("/".join(args)) + "/"
    #print pattern, s
    return bool(pat.search(s))

def test_ns_path(path, args):
    #print "**** test_path", repr(path), repr(args)
    pattern = to_regexp(path,
                        namespaces = {
        "xml": "http://www.w3.org/XML/1998/namespace",
        "das2": "http://biodas.org/documents/das2"},
                        # the empty namespace is not the same as no namespace!
                        default_namespace = "")
        
    pat = re.compile(pattern)
    s = "/" + ("/".join(args)) + "/"
    #print pattern, s
    return bool(pat.search(s))

def test_syntax():
    for (xpath, tag_list, expect) in (
           ("A", ["A"], 1),
           ("A", ["AA"], 0),
           ("A", ["B", "A"], 1),
           ("/A", ["B", "A"], 0),
           ("/B", ["B", "A"], 0),
           ("//A", ["B", "A"], 1),
           ("A//B", ["A", "B"], 1),
           ("A//B", ["C", "A", "B"], 1),
           ("/A//B", ["C", "A", "B"], 0),
           ("/B/*", ["B", "A"], 1),
           # Test back-tracking; both greedy and non-greedy cases
           ("A//B//C//D", ["A", "B", "C", "B", "D"], 1),
           ("A//B/D", ["A", "B", "C", "B", "D"], 1),

           # Clark namespace tests
           ("{http://x.com}A", ["{http://x.com}A"], 1),
           ("{http://x.org}A", ["{http://x.com}A"], 0),
           ("{http://x.org}A", ["{http://x.com}B", "{http://x.org}A"], 1),
           ("*", ["{http://x.com}A"], 1),
           ("{http://x.com}*", ["{http://x.com}A"], 1),
           ("{http://x.com}*", ["{http://x.org}A"], 0),
           
           ):
        got = test_path(xpath, tag_list)
        if got != expect:
            raise AssertionError("xpath %r against %r got %r, expected %r" %
                                 (xpath, tag_list, got, bool(expect)))

    for (xpath, tag_list, expect) in (
           # various namespace checks
           ("xml:A", ["{http://www.w3.org/XML/1998/namespace}A"], 1),
           ("xml:A", ["{http://www.w3.org/XML/1998/namespace2}A"], 0),
           ("xml:A", ["{http://www.w3.org/XML/1998/namespace}AA"], 0),
           ("xml:A", ["{http://www.w3.org/XML/1998/namespace}B",
                      "{http://www.w3.org/XML/1998/namespace}A"], 1),
           ("xml:B", ["{http://www.w3.org/XML/1998/namespace}B",
                      "{http://www.w3.org/XML/1998/namespace}A"], 0),

           ("A", ["{}A"], 1),
           ("A", ["A"], 0),

           ("*", ["A"], 0),
           ("*", ["{}A"], 1),
           ("das2:*", ["{http://biodas.org/documents/das2}AAA"], 1),
           ("das2:*", ["{}AAA"], 0),
           ("xml:*/das2:*", ["{http://www.w3.org/XML/1998/namespace}ABC",
                             "{http://biodas.org/documents/das2}ABC"], 1),
           ("das2:*/xml:*", ["{http://www.w3.org/XML/1998/namespace}ABC",
                             "{http://biodas.org/documents/das2}ABC"], 0),
           

           ):
        got = test_ns_path(xpath, tag_list)
        if got != expect:
            raise AssertionError("xpath %r against %r got %r, expected %r" %
                                 (xpath, tag_list, got, bool(expect)))

def test_filtering():
    import io as StringIO
    f = StringIO.StringIO("""\
 <A><AA>
   <B xmlns="http://z/"><C/><spam:D xmlns:spam="http://spam/">eggs</spam:D></B>
   <B x='6'>foo<B y='7'>bar</B>baz</B>
 </AA></A>""")
    special = object()
    class Capture(object):
        def __init__(self):
            self.history = []
        def __call__(self, event, ele, state):
            if state is not special:
                raise AssertionError("Did not get expected state")
            self.history.append( (event, ele) )

    filter = IterParseFilter()
    capture_all = Capture()
    filter.on_start_document(capture_all)
    filter.on_start("*", capture_all)
    filter.on_end("*", capture_all)
    filter.on_end_document(capture_all)
    filter.on_start_ns(capture_all)
    filter.on_end_ns(capture_all)

    for x in filter.parse(f, state=special):
        raise AssertionError("should not yield %r" % (x,))

    expect_history = (
        ("start-document", None),
        ("start", "A"),
        ("start", "AA"),
        ("start-ns", ("", "http://z/")),
        ("start", "{http://z/}B"),
        ("start", "{http://z/}C"),
        ("end", "{http://z/}C"),
        ("start-ns", ("spam", "http://spam/")),
        ("start", "{http://spam/}D"),
        ("end", "{http://spam/}D"),
        ("end-ns", None),
        ("end", "{http://z/}B"),
        ("end-ns", None),
        ("start", "B"),
        ("start", "B"),
        ("end", "B"),
        ("end", "B"),
        ("end", "AA"),
        ("end","A"),
        ("end-document", None),
        )

    for (got, expect) in zip(capture_all.history, expect_history):
        event, ele = got
        tag = getattr(ele, "tag", ele)
        if (event, tag) != expect:
            raise AssertionError("Expected %r Got %r" % (expect, (event, tag)))
    if len(capture_all.history) != len(expect_history):
        raise AssertionError("Length mismatch")
            
    f.seek(0)
    filter = IterParseFilter()
    def must_match_B(event, ele, state):
        if ele.tag != "B":
            raise AssertionError("%r is not B" % (ele.tag,))
    def must_match_B_y7(event, ele, state):
        if ele.tag != "B":
            raise AssertionError("%r is not B" % (ele.tag,))
        if ele.attrib["y"] != "7":
            raise AssertionError("%r is not the correct B" % (ele.tag,))

    filter.on_start("B", must_match_B)
    filter.on_start("B/B", must_match_B_y7)
    
    f.seek


def test_parse():
    import os
    filename = "/Users/dalke/Music/iTunes/iTunes Music Library.xml"
    if not os.path.exists(filename):
        print ("Cannot find %r: skipping test" % (filename,))
        return

    # Work through callbacks
    ef = IterParseFilter()
    def print_info(event, ele, state):
        d = {}
        children = iter(ele)
        for child in children:
            key = child.text
            value = children.next().text
            d[key] = value
        print ("%r is by %r" % (d["Name"], d.get("Artist", "<unknown>")))
        ele.clear()
            
    ef.on_end("/plist/dict/dict/dict", print_info)
    ef.handler_parse(open(filename))

    # Work through iterators
    ef = IterParseFilter()
    ef.iter_end("/plist/dict/dict/dict")
    for (event, ele) in ef.iterparse(open(filename)):
        d = {}
        children = iter(ele)
        for child in children:
            key = child.text
            value = children.next().text
            d[key] = value
        print ("%r is a %r song" % (d["Name"], d.get("Genre", "<unknown>")))
        ele.clear()
            

def test():
    test_syntax()
    test_filtering()
    test_parse()

if __name__ == "__main__":
    test()
    print ("All tests passed.")
