import pathlib
import typing

@typing.final
class BlankNode:
    """An RDF `blank node <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node>`_.

    :param value: the `blank node ID <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_ (if not present, a random blank node ID is automatically generated).
    :raises ValueError: if the blank node ID is invalid according to NTriples, Turtle, and SPARQL grammars.

    The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(BlankNode('ex'))
    '_:ex'"""

    value: str
    "the `blank node ID <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_."

    def __init__(self, value: typing.Union[str, None] = None) -> None:
        """An RDF `blank node <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node>`_.

        :param value: the `blank node ID <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_ (if not present, a random blank node ID is automatically generated).
        :raises ValueError: if the blank node ID is invalid according to NTriples, Turtle, and SPARQL grammars.

        The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(BlankNode('ex'))
        '_:ex'"""
    def __copy__(self) -> BlankNode: ...
    def __deepcopy__(self, memo: typing.Any) -> BlankNode: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = ("value",)

@typing.final
class DefaultGraph:
    """The RDF `default graph name <https://www.w3.org/TR/rdf11-concepts/#dfn-default-graph>`_."""

    value: str
    "the empty string."

    def __init__(self) -> None:
        """The RDF `default graph name <https://www.w3.org/TR/rdf11-concepts/#dfn-default-graph>`_."""
    def __copy__(self) -> DefaultGraph: ...
    def __deepcopy__(self, memo: typing.Any) -> DefaultGraph: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""

@typing.final
class Literal:
    """An RDF `literal <https://www.w3.org/TR/rdf11-concepts/#dfn-literal>`_.

    :param value: the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_.
    :param datatype: the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_.
    :param language: the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_.
    :raises ValueError: if the language tag is not valid according to `RFC 5646 <https://tools.ietf.org/rfc/rfc5646>`_ (`BCP 47 <https://tools.ietf.org/rfc/bcp/bcp47>`_).

    The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Literal('example'))
    '"example"'
    >>> str(Literal('example', language='en'))
    '"example"@en'
    >>> str(Literal('11', datatype=NamedNode('http://www.w3.org/2001/XMLSchema#integer')))
    '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'"""

    datatype: NamedNode
    "the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_."
    language: typing.Union[str, None]
    "the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_."
    value: str
    "the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_."

    def __init__(
        self,
        value: str,
        *,
        datatype: typing.Union[NamedNode, None] = None,
        language: typing.Union[str, None] = None,
    ) -> None:
        """An RDF `literal <https://www.w3.org/TR/rdf11-concepts/#dfn-literal>`_.

        :param value: the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_.
        :param datatype: the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_.
        :param language: the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_.
        :raises ValueError: if the language tag is not valid according to `RFC 5646 <https://tools.ietf.org/rfc/rfc5646>`_ (`BCP 47 <https://tools.ietf.org/rfc/bcp/bcp47>`_).

        The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Literal('example'))
        '"example"'
        >>> str(Literal('example', language='en'))
        '"example"@en'
        >>> str(Literal('11', datatype=NamedNode('http://www.w3.org/2001/XMLSchema#integer')))
        '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'"""
    def __copy__(self) -> Literal: ...
    def __deepcopy__(self, memo: typing.Any) -> Literal: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getnewargs_ex__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = ("value",)

@typing.final
class NamedNode:
    """An RDF `node identified by an IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-iri>`_.

    :param value: the IRI as a string.
    :raises ValueError: if the IRI is not valid according to `RFC 3987 <https://tools.ietf.org/rfc/rfc3987>`_.

    The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(NamedNode('http://example.com'))
    '<http://example.com>'"""

    value: str
    "the named node IRI."

    def __init__(self, value: str) -> None:
        """An RDF `node identified by an IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-iri>`_.

        :param value: the IRI as a string.
        :raises ValueError: if the IRI is not valid according to `RFC 3987 <https://tools.ietf.org/rfc/rfc3987>`_.

        The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(NamedNode('http://example.com'))
        '<http://example.com>'"""
    def __copy__(self) -> NamedNode: ...
    def __deepcopy__(self, memo: typing.Any) -> NamedNode: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = ("value",)

@typing.final
class Quad:
    """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.
    in a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

    :param subject: the quad subject.
    :param predicate: the quad predicate.
    :param object: the quad object.
    :param graph_name: the quad graph name. If not present, the default graph is assumed.

    The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
    '<http://example.com> <http://example.com/p> "1" <http://example.com/g>'

    >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), DefaultGraph()))
    '<http://example.com> <http://example.com/p> "1"'

    A quad could also be easily destructed into its components:

    >>> (s, p, o, g) = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))
    """

    graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph]
    "the quad graph name."
    object: typing.Union[NamedNode, BlankNode, Literal, Triple]
    "the quad object."
    predicate: NamedNode
    "the quad predicate."
    subject: typing.Union[NamedNode, BlankNode, Triple]
    "the quad subject."
    triple: Triple
    "the quad underlying triple."

    def __init__(
        self,
        subject: typing.Union[NamedNode, BlankNode, Triple],
        predicate: NamedNode,
        object: typing.Union[NamedNode, BlankNode, Literal, Triple],
        graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph, None] = None,
    ) -> None:
        """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.
        in a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

        :param subject: the quad subject.
        :param predicate: the quad predicate.
        :param object: the quad object.
        :param graph_name: the quad graph name. If not present, the default graph is assumed.

        The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        '<http://example.com> <http://example.com/p> "1" <http://example.com/g>'

        >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), DefaultGraph()))
        '<http://example.com> <http://example.com/p> "1"'

        A quad could also be easily destructed into its components:

        >>> (s, p, o, g) = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))
        """
    def __copy__(self) -> Quad: ...
    def __deepcopy__(self, memo: typing.Any) -> Quad: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getitem__(self, key: typing.Any) -> typing.Any:
        """Return self[key]."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __len__(self) -> int:
        """Return len(self)."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = (
        "subject",
        "predicate",
        "object",
        "graph_name",
    )

@typing.final
class QuerySolution:
    """Tuple associating variables and terms that are the result of a SPARQL ``SELECT`` query.

    It is the equivalent of a row in SQL.

    It could be indexes by variable name (:py:class:`Variable` or :py:class:`str`) or position in the tuple (:py:class:`int`).
    Unpacking also works.

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> solution = next(store.query('SELECT ?s ?p ?o WHERE { ?s ?p ?o }'))
    >>> solution[Variable('s')]
    <NamedNode value=http://example.com>
    >>> solution['s']
    <NamedNode value=http://example.com>
    >>> solution[0]
    <NamedNode value=http://example.com>
    >>> s, p, o = solution
    >>> s
    <NamedNode value=http://example.com>"""

    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getitem__(self, key: typing.Any) -> typing.Any:
        """Return self[key]."""
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __len__(self) -> int:
        """Return len(self)."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""

@typing.final
class QuerySolutions:
    """An iterator of :py:class:`QuerySolution` returned by a SPARQL ``SELECT`` query

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> list(store.query('SELECT ?s WHERE { ?s ?p ?o }'))
    [<QuerySolution s=<NamedNode value=http://example.com>>]"""

    variables: typing.List[Variable]
    "the ordered list of all variables that could appear in the query results"

    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __next__(self) -> typing.Any:
        """Implement next(self)."""

@typing.final
class QueryTriples:
    """An iterator of :py:class:`Triple` returned by a SPARQL ``CONSTRUCT`` or ``DESCRIBE`` query

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> list(store.query('CONSTRUCT WHERE { ?s ?p ?o }'))
    [<Triple subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]
    """

    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __next__(self) -> typing.Any:
        """Implement next(self)."""

@typing.final
class Store:
    """RDF store.

    It encodes a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_ and allows to query it using SPARQL.
    It is based on the `RocksDB <https://rocksdb.org/>`_ key-value database.

    This store ensures the "repeatable read" isolation level: the store only exposes changes that have
    been "committed" (i.e. no partial writes) and the exposed state does not change for the complete duration
    of a read operation (e.g. a SPARQL query) or a read/write operation (e.g. a SPARQL update).

    The :py:class:`Store` constructor opens a read-write instance.
    To open a static read-only instance use :py:func:`Store.read_only`
    and to open a read-only instance that tracks a read-write instance use :py:func:`Store.secondary`.

    :param path: the path of the directory in which the store should read and write its data. If the directory does not exist, it is created.
    If no directory is provided a temporary one is created and removed when the Python garbage collector removes the store.
    In this case, the store data are kept in memory and never written on disk.
    :raises IOError: if the target directory contains invalid data or could not be accessed.

    The :py:func:`str` function provides a serialization of the store in NQuads:

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
    >>> str(store)
    '<http://example.com> <http://example.com/p> "1" <http://example.com/g> .\\n'"""

    def __init__(self, path: typing.Union[str, pathlib.Path, None] = None) -> None:
        """RDF store.

        It encodes a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_ and allows to query it using SPARQL.
        It is based on the `RocksDB <https://rocksdb.org/>`_ key-value database.

        This store ensures the "repeatable read" isolation level: the store only exposes changes that have
        been "committed" (i.e. no partial writes) and the exposed state does not change for the complete duration
        of a read operation (e.g. a SPARQL query) or a read/write operation (e.g. a SPARQL update).

        The :py:class:`Store` constructor opens a read-write instance.
        To open a static read-only instance use :py:func:`Store.read_only`
        and to open a read-only instance that tracks a read-write instance use :py:func:`Store.secondary`.

        :param path: the path of the directory in which the store should read and write its data. If the directory does not exist, it is created.
        If no directory is provided a temporary one is created and removed when the Python garbage collector removes the store.
        In this case, the store data are kept in memory and never written on disk.
        :raises IOError: if the target directory contains invalid data or could not be accessed.

        The :py:func:`str` function provides a serialization of the store in NQuads:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> str(store)
        '<http://example.com> <http://example.com/p> "1" <http://example.com/g> .\\n'"""
    def add(self, quad: Quad) -> None:
        """Adds a quad to the store.

        :param quad: the quad to add.
        :raises IOError: if an I/O error happens during the quad insertion.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def add_graph(
        self, graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph]
    ) -> None:
        """Adds a named graph to the store.

        :param graph_name: the name of the name graph to add.
        :raises IOError: if an I/O error happens during the named graph insertion.

        >>> store = Store()
        >>> store.add_graph(NamedNode('http://example.com/g'))
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""
    def backup(self, target_directory: str) -> None:
        """Creates database backup into the `target_directory`.

        After its creation, the backup is usable using :py:class:`Store` constructor.
        like a regular pyxigraph database and operates independently from the original database.

        Warning: Backups are only possible for on-disk databases created by providing a path to :py:class:`Store` constructor.
        Temporary in-memory databases created without path are not compatible with the backup system.

        Warning: An error is raised if the ``target_directory`` already exists.

        If the target directory is in the same file system as the current database,
        the database content will not be fully copied
        but hard links will be used to point to the original database immutable snapshots.
        This allows cheap regular backups.

        If you want to move your data to another RDF storage system, you should have a look at the :py:func:`dump_dataset` function instead.

        :param target_directory: the directory name to save the database to.
        :raises IOError: if an I/O error happens during the backup."""
    def bulk_extend(self, quads: typing.Iterable[Quad]) -> None:
        """Adds a set of quads to this store.

        This function is designed to be as fast as possible **without** transactional guarantees.
        Only a part of the data might be written to the store.

        :param quads: the quads to add.
        :raises IOError: if an I/O error happens during the quad insertion.

        >>> store = Store()
        >>> store.bulk_extend([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def bulk_load(
        self,
        input: typing.Union[typing.IO[bytes], typing.IO[str], str, pathlib.Path],
        mime_type: str,
        *,
        base_iri: typing.Union[str, None] = None,
        to_graph: typing.Union[NamedNode, BlankNode, DefaultGraph, None] = None,
    ) -> None:
        """Loads an RDF serialization into the store.

        This function is designed to be as fast as possible on big files **without** transactional guarantees.
        If the file is invalid only a piece of it might be written to the store.

        The :py:func:`load` method is also available for loads with transactional guarantees.

        It currently supports the following formats:

        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (``application/n-triples``)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (``application/n-quads``)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (``text/turtle``)
        * `TriG <https://www.w3.org/TR/trig/>`_ (``application/trig``)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (``application/rdf+xml``)

        It supports also some MIME type aliases.
        For example, ``application/turtle`` could also be used for `Turtle <https://www.w3.org/TR/turtle/>`_
        and ``application/xml`` for `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_.

        :param input: The binary I/O object or file path to read from. For example, it could be a file path as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
        :param mime_type: the MIME type of the RDF serialization.
        :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
        :param to_graph: if it is a file composed of triples, the graph in which the triples should be stored. By default, the default graph is used.
        :raises ValueError: if the MIME type is not supported or the `to_graph` parameter is given with a quad file.
        :raises SyntaxError: if the provided data is invalid.
        :raises IOError: if an I/O error happens during a quad insertion.

        >>> store = Store()
        >>> store.bulk_load(io.BytesIO(b'<foo> <p> "1" .'), "text/turtle", base_iri="http://example.com/", to_graph=NamedNode("http://example.com/g"))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def clear(self) -> None:
        """Clears the store by removing all its contents.

        :raises IOError: if an I/O error happens during the operation.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.clear()
        >>> list(store)
        []
        >>> list(store.named_graphs())
        []"""
    def clear_graph(
        self, graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph]
    ) -> None:
        """Clears a graph from the store without removing it.

        :param graph_name: the name of the name graph to clear.
        :raises IOError: if an I/O error happens during the operation.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.clear_graph(NamedNode('http://example.com/g'))
        >>> list(store)
        []
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""
    def contains_named_graph(
        self, graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph]
    ) -> bool:
        """Returns if the store contains the given named graph.

        :param graph_name: the name of the named graph.
        :raises IOError: if an I/O error happens during the named graph lookup.

        >>> store = Store()
        >>> store.add_graph(NamedNode('http://example.com/g'))
        >>> store.contains_named_graph(NamedNode('http://example.com/g'))
        True"""
    def dump(
        self,
        output: typing.Union[typing.IO[bytes], str, pathlib.Path],
        mime_type: str,
        *,
        from_graph: typing.Union[NamedNode, BlankNode, DefaultGraph, None] = None,
    ) -> None:
        """Dumps the store quads or triples into a file.

        It currently supports the following formats:

        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (``application/n-triples``)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (``application/n-quads``)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (``text/turtle``)
        * `TriG <https://www.w3.org/TR/trig/>`_ (``application/trig``)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (``application/rdf+xml``)

        It supports also some MIME type aliases.
        For example, ``application/turtle`` could also be used for `Turtle <https://www.w3.org/TR/turtle/>`_
        and ``application/xml`` for `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_.

        :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``.
        :param mime_type: the MIME type of the RDF serialization.
        :param from_graph: if a triple based format is requested, the store graph from which dump the triples. By default, the default graph is used.
        :raises ValueError: if the MIME type is not supported or the `from_graph` parameter is given with a quad syntax.
        :raises IOError: if an I/O error happens during a quad lookup

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> output = io.BytesIO()
        >>> store.dump(output, "text/turtle", from_graph=NamedNode("http://example.com/g"))
        >>> output.getvalue()
        b'<http://example.com> <http://example.com/p> "1" .\\n'"""
    def extend(self, quads: typing.Iterable[Quad]) -> None:
        """Adds atomically a set of quads to this store.

        Insertion is done in a transactional manner: either the full operation succeeds or nothing is written to the database.
        The :py:func:`bulk_extend` method is also available for much faster loading of a large number of quads but without transactional guarantees.

        :param quads: the quads to add.
        :raises IOError: if an I/O error happens during the quad insertion.

        >>> store = Store()
        >>> store.extend([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def flush(self) -> None:
        """Flushes all buffers and ensures that all writes are saved on disk.

        Flushes are automatically done using background threads but might lag a little bit.

        :raises IOError: if an I/O error happens during the flush."""
    def load(
        self,
        input: typing.Union[typing.IO[bytes], typing.IO[str], str, pathlib.Path],
        mime_type: str,
        *,
        base_iri: typing.Union[str, None] = None,
        to_graph: typing.Union[NamedNode, BlankNode, DefaultGraph, None] = None,
    ) -> None:
        """Loads an RDF serialization into the store.

        Loads are applied in a transactional manner: either the full operation succeeds or nothing is written to the database.
        The :py:func:`bulk_load` method is also available for much faster loading of big files but without transactional guarantees.

        Beware, the full file is loaded into memory.

        It currently supports the following formats:

        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (``application/n-triples``)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (``application/n-quads``)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (``text/turtle``)
        * `TriG <https://www.w3.org/TR/trig/>`_ (``application/trig``)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (``application/rdf+xml``)

        It supports also some MIME type aliases.
        For example, ``application/turtle`` could also be used for `Turtle <https://www.w3.org/TR/turtle/>`_
        and ``application/xml`` for `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_.

        :param input: The binary I/O object or file path to read from. For example, it could be a file path as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
        :param mime_type: the MIME type of the RDF serialization.
        :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
        :param to_graph: if it is a file composed of triples, the graph in which the triples should be stored. By default, the default graph is used.
        :raises ValueError: if the MIME type is not supported or the `to_graph` parameter is given with a quad file.
        :raises SyntaxError: if the provided data is invalid.
        :raises IOError: if an I/O error happens during a quad insertion.

        >>> store = Store()
        >>> store.load(io.BytesIO(b'<foo> <p> "1" .'), "text/turtle", base_iri="http://example.com/", to_graph=NamedNode("http://example.com/g"))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def named_graphs(self) -> typing.Iterator[typing.Union[NamedNode, BlankNode]]:
        """Returns an iterator over all the store named graphs.

        :return: an iterator of the store graph names.
        :raises IOError: if an I/O error happens during the named graphs lookup.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""
    def optimize(self) -> None:
        """Optimizes the database for future workload.

        Useful to call after a batch upload or another similar operation.

        :raises IOError: if an I/O error happens during the optimization."""
    def quads_for_pattern(
        self,
        subject: typing.Union[NamedNode, BlankNode, Triple, None],
        predicate: typing.Union[NamedNode, None],
        object: typing.Union[NamedNode, BlankNode, Literal, Triple, None],
        graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph, None] = None,
    ) -> typing.Iterator[Quad]:
        """Looks for the quads matching a given pattern.

        :param subject: the quad subject or :py:const:`None` to match everything.
        :param predicate: the quad predicate or :py:const:`None` to match everything.
        :param object: the quad object or :py:const:`None` to match everything.
        :param graph_name: the quad graph name. To match only the default graph, use :py:class:`DefaultGraph`. To match everything use :py:const:`None`.
        :return: an iterator of the quads matching the pattern.
        :raises IOError: if an I/O error happens during the quads lookup.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store.quads_for_pattern(NamedNode('http://example.com'), None, None, None))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]
        """
    def query(
        self,
        query: str,
        *,
        base_iri: typing.Union[str, None] = None,
        use_default_graph_as_union: bool = False,
        default_graph: typing.Union[
            NamedNode,
            BlankNode,
            DefaultGraph,
            typing.List[typing.Union[NamedNode, BlankNode, DefaultGraph]],
            None,
        ] = None,
        named_graphs: typing.Union[
            typing.List[typing.Union[NamedNode, BlankNode]], None
        ] = None,
    ) -> typing.Union[QuerySolutions, QueryTriples, bool]:
        """Executes a `SPARQL 1.1 query <https://www.w3.org/TR/sparql11-query/>`_.

        :param query: the query to execute.
        :param base_iri: the base IRI used to resolve the relative IRIs in the SPARQL query or :py:const:`None` if relative IRI resolution should not be done.
        :param use_default_graph_as_union: if the SPARQL query should look for triples in all the dataset graphs by default (i.e. without `GRAPH` operations). Disabled by default.
        :param default_graph: list of the graphs that should be used as the query default graph. By default, the store default graph is used.
        :param named_graphs: list of the named graphs that could be used in SPARQL `GRAPH` clause. By default, all the store named graphs are available.
        :return: a :py:class:`bool` for ``ASK`` queries, an iterator of :py:class:`Triple` for ``CONSTRUCT`` and ``DESCRIBE`` queries and an iterator of :py:class:`QuerySolution` for ``SELECT`` queries.
        :raises SyntaxError: if the provided query is invalid.
        :raises IOError: if an I/O error happens while reading the store.

        ``SELECT`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> [solution['s'] for solution in store.query('SELECT ?s WHERE { ?s ?p ?o }')]
        [<NamedNode value=http://example.com>]

        ``CONSTRUCT`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> list(store.query('CONSTRUCT WHERE { ?s ?p ?o }'))
        [<Triple subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]

        ``ASK`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.query('ASK { ?s ?p ?o }')
        True"""
    @staticmethod
    def read_only(path: str) -> Store:
        """Opens a read-only store from disk.

        Opening as read-only while having an other process writing the database is undefined behavior.
        :py:func:`Store.secondary` should be used in this case.

        :param path: path to the primary read-write instance data.
        :return: the opened store.
        :raises IOError: if the target directory contains invalid data or could not be accessed.
        """
    def remove(self, quad: Quad) -> None:
        """Removes a quad from the store.

        :param quad: the quad to remove.
        :raises IOError: if an I/O error happens during the quad removal.

        >>> store = Store()
        >>> quad = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))
        >>> store.add(quad)
        >>> store.remove(quad)
        >>> list(store)
        []"""
    def remove_graph(
        self, graph_name: typing.Union[NamedNode, BlankNode, DefaultGraph]
    ) -> None:
        """Removes a graph from the store.

        The default graph will not be removed but just cleared.

        :param graph_name: the name of the name graph to remove.
        :raises IOError: if an I/O error happens during the named graph removal.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.remove_graph(NamedNode('http://example.com/g'))
        >>> list(store.named_graphs())
        []"""
    @staticmethod
    def secondary(
        primary_path: str, secondary_path: typing.Union[str, None] = None
    ) -> Store:
        """Opens a read-only clone of a running read-write store.

        Changes done while this process is running will be replicated after a possible lag.

        It should only be used if a primary instance opened with :py:func:`Store` is running at the same time.

        If you want to simple read-only store use :py:func:`Store.read_only`.

        :param primary_path: path to the primary read-write instance data.
        :param secondary_path: path to an other directory for the secondary instance cache. If not given a temporary directory will be used.
        :return: the opened store.
        :raises IOError: if the target directories contain invalid data or could not be accessed.
        """
    def update(self, update: str, *, base_iri: typing.Union[str, None] = None) -> None:
        """Executes a `SPARQL 1.1 update <https://www.w3.org/TR/sparql11-update/>`_.

        Updates are applied in a transactional manner: either the full operation succeeds or nothing is written to the database.

        :param update: the update to execute.
        :param base_iri: the base IRI used to resolve the relative IRIs in the SPARQL update or :py:const:`None` if relative IRI resolution should not be done.
        :raises SyntaxError: if the provided update is invalid.
        :raises IOError: if an I/O error happens while reading the store.

        ``INSERT DATA`` update:

        >>> store = Store()
        >>> store.update('INSERT DATA { <http://example.com> <http://example.com/p> "1" }')
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<DefaultGraph>>]

        ``DELETE DATA`` update:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.update('DELETE DATA { <http://example.com> <http://example.com/p> "1" }')
        >>> list(store)
        []

        ``DELETE`` update:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.update('DELETE WHERE { <http://example.com> ?p ?o }')
        >>> list(store)
        []"""
    def __bool__(self) -> bool:
        """True if self else False"""
    def __contains__(self, key: typing.Any) -> bool:
        """Return key in self."""
    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __len__(self) -> int:
        """Return len(self)."""
    def __str__(self) -> str:
        """Return str(self)."""

@typing.final
class Triple:
    """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.

    :param subject: the triple subject.
    :param predicate: the triple predicate.
    :param object: the triple object.

    The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    '<http://example.com> <http://example.com/p> "1"'

    A triple could also be easily destructed into its components:

    >>> (s, p, o) = Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))
    """

    object: typing.Union[NamedNode, BlankNode, Literal, Triple]
    "the triple object."
    predicate: NamedNode
    "the triple predicate."
    subject: typing.Union[NamedNode, BlankNode, Triple]
    "the triple subject."

    def __init__(
        self,
        subject: typing.Union[NamedNode, BlankNode, Triple],
        predicate: NamedNode,
        object: typing.Union[NamedNode, BlankNode, Literal, Triple],
    ) -> None:
        """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.

        :param subject: the triple subject.
        :param predicate: the triple predicate.
        :param object: the triple object.

        The :py:func:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        '<http://example.com> <http://example.com/p> "1"'

        A triple could also be easily destructed into its components:

        >>> (s, p, o) = Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))
        """
    def __copy__(self) -> Triple: ...
    def __deepcopy__(self, memo: typing.Any) -> Triple: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getitem__(self, key: typing.Any) -> typing.Any:
        """Return self[key]."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __iter__(self) -> typing.Any:
        """Implement iter(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __len__(self) -> int:
        """Return len(self)."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = ("subject", "predicate", "object")

@typing.final
class Variable:
    """A SPARQL query variable.

    :param value: the variable name as a string.
    :raises ValueError: if the variable name is invalid according to the SPARQL grammar.

    The :py:func:`str` function provides a serialization compatible with SPARQL:

    >>> str(Variable('foo'))
    '?foo'"""

    value: str
    "the variable name."

    def __init__(self, value: str) -> None:
        """A SPARQL query variable.

        :param value: the variable name as a string.
        :raises ValueError: if the variable name is invalid according to the SPARQL grammar.

        The :py:func:`str` function provides a serialization compatible with SPARQL:

        >>> str(Variable('foo'))
        '?foo'"""
    def __copy__(self) -> Variable: ...
    def __deepcopy__(self, memo: typing.Any) -> Variable: ...
    def __eq__(self, value: typing.Any) -> bool:
        """Return self==value."""
    def __ge__(self, value: typing.Any) -> bool:
        """Return self>=value."""
    def __getnewargs__(self) -> typing.Any: ...
    def __gt__(self, value: typing.Any) -> bool:
        """Return self>value."""
    def __hash__(self) -> int:
        """Return hash(self)."""
    def __le__(self, value: typing.Any) -> bool:
        """Return self<=value."""
    def __lt__(self, value: typing.Any) -> bool:
        """Return self<value."""
    def __ne__(self, value: typing.Any) -> bool:
        """Return self!=value."""
    def __repr__(self) -> str:
        """Return repr(self)."""
    def __str__(self) -> str:
        """Return str(self)."""
    __match_args__: typing.Tuple[str, ...] = ("value",)

def parse(
    input: typing.Union[typing.IO[bytes], typing.IO[str], str, pathlib.Path],
    mime_type: str,
    *,
    base_iri: typing.Union[str, None] = None,
) -> typing.Union[typing.Iterator[Triple], typing.Iterator[Quad]]:
    """Parses RDF graph and dataset serialization formats.

    It currently supports the following formats:

    * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (``application/n-triples``)
    * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (``application/n-quads``)
    * `Turtle <https://www.w3.org/TR/turtle/>`_ (``text/turtle``)
    * `TriG <https://www.w3.org/TR/trig/>`_ (``application/trig``)
    * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (``application/rdf+xml``)

    It supports also some MIME type aliases.
    For example, ``application/turtle`` could also be used for `Turtle <https://www.w3.org/TR/turtle/>`_
    and ``application/xml`` for `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_.

    :param input: The binary I/O object or file path to read from. For example, it could be a file path as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
    :param mime_type: the MIME type of the RDF serialization.
    :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
    :return: an iterator of RDF triples or quads depending on the format.
    :raises ValueError: if the MIME type is not supported.
    :raises SyntaxError: if the provided data is invalid.

    >>> input = io.BytesIO(b'<foo> <p> "1" .')
    >>> list(parse(input, "text/turtle", base_iri="http://example.com/"))
    [<Triple subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]
    """

def serialize(
    input: typing.Union[typing.Iterable[Triple], typing.Iterable[Quad]],
    output: typing.Union[typing.IO[bytes], str, pathlib.Path],
    mime_type: str,
) -> None:
    """Serializes an RDF graph or dataset.

    It currently supports the following formats:

    * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (``application/n-triples``)
    * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (``application/n-quads``)
    * `Turtle <https://www.w3.org/TR/turtle/>`_ (``text/turtle``)
    * `TriG <https://www.w3.org/TR/trig/>`_ (``application/trig``)
    * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (``application/rdf+xml``)

    It supports also some MIME type aliases.
    For example, ``application/turtle`` could also be used for `Turtle <https://www.w3.org/TR/turtle/>`_
    and ``application/xml`` for `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_.

    :param input: the RDF triples and quads to serialize.
    :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``.
    :param mime_type: the MIME type of the RDF serialization.
    :raises ValueError: if the MIME type is not supported.
    :raises TypeError: if a triple is given during a quad format serialization or reverse.

    >>> output = io.BytesIO()
    >>> serialize([Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))], output, "text/turtle")
    >>> output.getvalue()
    b'<http://example.com> <http://example.com/p> "1" .\\n'"""
