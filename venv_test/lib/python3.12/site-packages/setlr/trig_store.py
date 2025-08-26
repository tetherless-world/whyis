import logging
from threading import Thread
from os.path import exists, abspath
from os import mkdir
from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.term import URIRef
from urllib.request import pathname2url
from rdflib import ConjunctiveGraph
from rdflib.term import BNode

def bb(u):
    return u.encode("utf-8")


class TrigStore(Store):
    """\
    """

    context_aware = True
    formula_aware = True
    transaction_aware = False
    graph_aware = True
    db_env = None

    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        self.__identifier = identifier
        super(TrigStore, self).__init__(configuration)
        self.__namespace = {}
        self.__prefix = {}

    def __get_identifier(self):
        return self.__identifier

    identifier = property(__get_identifier)

    def _init_db_environment(self, file, create=True):
        file_obj = open(file, "a+")
        return file_obj

    def is_open(self):
        return self.__open

    def open(self, path, create=True):
        homeDir = path

        if self.__identifier is None:
            self.__identifier = URIRef(pathname2url(abspath(homeDir)))

        db_env = self._init_db_environment(homeDir, create)
        if db_env == NO_STORE:
            return NO_STORE
        self.db_env = db_env
        self.__open = True

        return VALID_STORE

    def sync(self):
        pass

    def close(self, commit_pending_transaction=False):
        self.__open = False
        self.db_env.close()

    def add(self, triple, context, quoted=False, txn=None):
        """\
        Add a triple to the store of triples.
        """
        (subject, predicate, object) = triple
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"
        value = "%s { %s %s %s .}\n" % (context.identifier.n3(), subject.n3(), predicate.n3(), object.n3())
        self.db_env.seek(0,2) # seek to end
        self.db_env.write(value)

    def __remove(self, spo, c, quoted=False, txn=None):
        pass

    def remove(self, spo, context, txn=None):
        pass

    def triples(self, spo, context=None, txn=None):
        """A generator over all the triples matching"""
        assert self.__open, "The Store must be open."

        if context is None or isinstance(context.identifier, BNode):
            c = None
        else:
            c = context.identifier
        subject, predicate, object = spo
        self.db_env.seek(0)
        for line in self.db_env:
            g = ConjunctiveGraph()
            g.parse(data=line, format="trig")

            for s, p, o, ctx in g.quads((None, None, None, None)):
                #print(s, p, o, ctx.identifier)
                if subject is not None and subject != s:
                    continue
                if predicate is not None and predicate != p:
                    continue
                if object is not None and object != o:
                    continue
                if c is not None :
                    if c != ctx.identifier:
                        continue
                yield (s, p, o), ctx.identifier

    def __len__(self, context=None):
        def blocks(files, size=65536):
            while True:
                b = files.read(size)
                if not b: break
                yield b

        self.db_env.seek(0)
        return (sum(bl.count("\n") for bl in blocks(self.db_env)))

    def contexts(self, triple=None):
        for context in []:
            yield context


    def add_graph(self, graph):
        pass

    def remove_graph(self, graph):
        pass

    def __ctx_to_str(self, ctx):
        if ctx is None:
            return None
        try:
            # ctx could be a graph. In that case, use its identifier
            ctx_str = "{}:{}".format(ctx.identifier.__class__.__name__, ctx.identifier)
            self.__context_obj_map[ctx_str] = ctx
            return ctx_str
        except AttributeError:
            # otherwise, ctx should be a URIRef or BNode or str
            if isinstance(ctx, str):
                ctx_str = "{}:{}".format(ctx.__class__.__name__, ctx)
                if ctx_str in self.__context_obj_map:
                    return ctx_str
                self.__context_obj_map[ctx_str] = ctx
                return ctx_str
            raise RuntimeError("Cannot use that type of object as a Graph context")

    def bind(self, prefix, namespace):
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        for prefix, namespace in self.__namespace.items():
            yield prefix, namespace
