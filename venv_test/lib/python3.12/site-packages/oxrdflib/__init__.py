import shutil

import pyoxigraph as ox
from rdflib import Graph
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.query import Result
from rdflib.store import VALID_STORE, Store
from rdflib.term import BNode, Literal, Node, URIRef, Variable

__all__ = ["OxigraphStore"]


class OxigraphStore(Store):
    context_aware = True
    formula_aware = False
    transaction_aware = False
    graph_aware = True

    def __init__(self, configuration=None, identifier=None):
        self._store = None
        self._prefix_for_namespace = {}
        self._namespace_for_prefix = {}
        super().__init__(configuration, identifier)

    def open(self, configuration, create=False):
        if self._store is not None:
            raise ValueError("The open function should be called before any RDF operation")
        self._store = ox.Store(configuration)
        return VALID_STORE

    def close(self, commit_pending_transaction=False):
        del self._store

    def destroy(self, configuration):
        shutil.rmtree(configuration)

    def gc(self):
        pass

    @property
    def _inner(self):
        if self._store is None:
            self._store = ox.Store()
        return self._store

    def add(self, triple, context, quoted=False):
        if quoted:
            raise ValueError("Oxigraph stores are not formula aware")
        self._inner.add(_to_ox(triple, context))
        super().add(triple, context, quoted)

    def remove(self, triple, context=None):
        for q in self._inner.quads_for_pattern(*_to_ox_quad_pattern(triple, context)):
            self._inner.remove(q)
        super().remove(triple, context)

    def triples(self, triple_pattern, context=None):
        return (_from_ox(q) for q in self._inner.quads_for_pattern(*_to_ox_quad_pattern(triple_pattern, context)))

    def __len__(self, context=None):
        if context is None:
            # TODO: very bad
            return len({q.triple for q in self._inner})
        else:
            return sum(1 for _ in self._inner.quads_for_pattern(None, None, None, _to_ox(context)))

    def contexts(self, triple=None):
        if triple is None:
            return (_from_ox(g) for g in self._inner.named_graphs())
        else:
            return (_from_ox(q[3]) for q in self._inner.quads_for_pattern(*_to_ox_quad_pattern(triple)))

    def query(self, query, initNs, initBindings, queryGraph, **kwargs):
        initNs = dict(self._namespace_for_prefix, **initNs)
        query = "".join(f"PREFIX {prefix}: <{namespace}>\n" for prefix, namespace in initNs.items()) + query
        if initBindings:
            query += "\nVALUES ( {} ) {{ ({}) }}".format(
                " ".join(f"?{k}" for k in initBindings.keys()), " ".join(v.n3() for v in initBindings.values())
            )
        result = self._inner.query(
            query,
            use_default_graph_as_union=queryGraph == "__UNION__",
            default_graph=_to_ox(queryGraph) if isinstance(queryGraph, Node) else None,
        )
        if isinstance(result, bool):
            out = Result("ASK")
            out.askAnswer = result
        elif isinstance(result, ox.QuerySolutions):
            out = Result("SELECT")
            out.vars = [Variable(v.value) for v in result.variables]
            out.bindings = ({v: _from_ox(val) for v, val in zip(out.vars, solution)} for solution in result)
        elif isinstance(result, ox.QueryTriples):
            out = Result("CONSTRUCT")
            out.graph = Graph()
            out.graph += (_from_ox(t) for t in result)
        else:
            raise ValueError(f"Unexpected query result: {result}")
        return out

    def update(self, update, initNs, initBindings, queryGraph, **kwargs):
        raise NotImplementedError

    def commit(self):
        # TODO: implement
        pass

    def rollback(self):
        # TODO: implement
        pass

    def add_graph(self, graph):
        self._inner.add_graph(_to_ox(graph))

    def remove_graph(self, graph):
        self._inner.remove_graph(_to_ox(graph))

    def bind(self, prefix, namespace):
        self._namespace_for_prefix[prefix] = namespace
        self._prefix_for_namespace[namespace] = prefix

    def prefix(self, namespace):
        return self._prefix_for_namespace.get(namespace)

    def namespace(self, prefix):
        return self._namespace_for_prefix.get(prefix)

    def namespaces(self):
        yield from self._namespace_for_prefix.items()


def _to_ox(term, context=None):
    if term is None:
        return None
    elif term == DATASET_DEFAULT_GRAPH_ID:
        return ox.DefaultGraph()
    elif isinstance(term, URIRef):
        return ox.NamedNode(term)
    elif isinstance(term, BNode):
        return ox.BlankNode(term)
    elif isinstance(term, Literal):
        return ox.Literal(term, language=term.language, datatype=ox.NamedNode(term.datatype) if term.datatype else None)
    elif isinstance(term, Graph):
        return _to_ox(term.identifier)
    elif isinstance(term, tuple):
        if len(term) == 3:
            return ox.Quad(_to_ox(term[0]), _to_ox(term[1]), _to_ox(term[2]), _to_ox(context))
        elif len(term) == 4:
            return ox.Quad(_to_ox(term[0]), _to_ox(term[1]), _to_ox(term[2]), _to_ox(term[3]))
        else:
            raise ValueError(f"Unexpected rdflib term: {repr(term)}")
    else:
        raise ValueError(f"Unexpected rdflib term: {repr(term)}")


def _to_ox_quad_pattern(triple, context=None):
    (s, p, o) = triple
    return _to_ox_term_pattern(s), _to_ox_term_pattern(p), _to_ox_term_pattern(o), _to_ox_term_pattern(context)


def _to_ox_term_pattern(term):
    if term is None:
        return None
    elif isinstance(term, URIRef):
        return ox.NamedNode(term)
    elif isinstance(term, BNode):
        return ox.BlankNode(term)
    elif isinstance(term, Literal):
        return ox.Literal(term, language=term.language, datatype=ox.NamedNode(term.datatype) if term.datatype else None)
    elif isinstance(term, Graph):
        return _to_ox(term.identifier)
    else:
        raise ValueError(f"Unexpected rdflib term: {repr(term)}")


def _from_ox(term):
    if term is None:
        return None
    elif isinstance(term, ox.NamedNode):
        return URIRef(term.value)
    elif isinstance(term, ox.BlankNode):
        return BNode(term.value)
    elif isinstance(term, ox.Literal):
        if term.language:
            return Literal(term.value, lang=term.language)
        else:
            return Literal(term.value, datatype=URIRef(term.datatype.value))
    elif isinstance(term, ox.DefaultGraph):
        return None
    elif isinstance(term, ox.Triple):
        return _from_ox(term.subject), _from_ox(term.predicate), _from_ox(term.object)
    elif isinstance(term, ox.Quad):
        return (_from_ox(term.subject), _from_ox(term.predicate), _from_ox(term.object)), _from_ox(term.graph_name)
    else:
        raise ValueError(f"Unexpected Oxigraph term: {repr(term)}")
