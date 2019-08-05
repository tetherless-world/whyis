from flask import current_app, request
from rdflib import URIRef, ConjunctiveGraph
import sadi.mimeparse

from whyis.data_formats import DATA_FORMATS


def get_nanopub_uri(ident):
    return URIRef('%s/pub/%s'%(current_app.config['lod_prefix'], ident))


def get_nanopub_graph():
    inputGraph = ConjunctiveGraph()
    contentType = request.headers['Content-Type']
    encoding = 'utf8' if not request.content_encoding else request.content_encoding
    content = str(request.data, encoding)
    fmt = sadi.mimeparse.best_match([mt for mt in list(DATA_FORMATS.keys()) if mt is not None],contentType)
    if fmt in DATA_FORMATS:
        inputGraph.parse(data=content, format=DATA_FORMATS[fmt])
    return inputGraph
