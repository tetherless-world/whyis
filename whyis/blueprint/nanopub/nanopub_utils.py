import markdown
from flask import current_app, request
from flask_login import current_user
from rdflib import URIRef, ConjunctiveGraph, Graph, Literal, RDF
import sadi.mimeparse

from whyis.data_formats import DATA_FORMATS
from whyis.namespace import NS
from whyis.datastore import create_id
from whyis.nanopub import Nanopublication


def get_nanopub_uri(ident):
    return current_app.nanopub_manager.prefix[ident]

graph_aware_formats = set([
    "json-ld",
    "trig",
    "nquads"
])

def load_nanopub_graph(format, location=None, data=None, store=None):
    if store is None:
        store = ConjunctiveGraph().store
    if format in graph_aware_formats:
        inputGraph = ConjunctiveGraph(store=store)
    else:
        nanopub = Nanopublication(store = store, identifier=current_app.nanopub_manager.prefix[create_id()])
        nanopub.nanopub_resource
        nanopub.assertion
        nanopub.provenance
        nanopub.pubinfo
        inputGraph = Graph(store=store, identifier=nanopub.assertion.identifier)
    inputGraph.parse(data=data, location=location, format=format, publicID=inputGraph.identifier)
    return ConjunctiveGraph(store=store)

def get_nanopub_graph():
    contentType = request.headers['Content-Type']
    encoding = 'utf8' if not request.content_encoding else request.content_encoding
    content = str(request.data, encoding)
    fmt = sadi.mimeparse.best_match([mt for mt in list(DATA_FORMATS.keys()) if mt is not None],contentType)
    if fmt in DATA_FORMATS:
        format = DATA_FORMATS[fmt]
        return load_nanopub_graph(format, data=content)
    else:
        return None

def prep_nanopub(nanopub):
    #nanopub = Nanopublication(store=graph.store, identifier=nanopub_uri)
    about = nanopub.nanopub_resource.value(NS.sio.isAbout)
    #print nanopub.assertion_resource.identifier, about
    _prep_graph(nanopub.assertion_resource, about.identifier if about is not None else None)
    #_prep_graph(nanopub.pubinfo_resource, nanopub.assertion_resource.identifier)
    _prep_graph(nanopub.provenance_resource, nanopub.assertion_resource.identifier)
    nanopub.pubinfo.add((nanopub.assertion.identifier, NS.dc.contributor, current_user.identifier))
    return nanopub


def _prep_graph(resource, about = None):
    #print '_prep_graph', resource.identifier, about
    content_type = resource.value(NS.ov.hasContentType)
    if content_type is not None:
        content_type = content_type.value
    #print 'graph content type', resource.identifier, content_type
    #print resource.graph.serialize(format="nquads")
    g = Graph(store=resource.graph.store,identifier=resource.identifier)
    text = resource.value(NS.prov.value)
    if content_type is not None and text is not None:
        #print 'Content type:', content_type, resource.identifier
        html = None
        if content_type in ["text/html", "application/xhtml+xml"]:
            html = Literal(text.value, datatype=RDF.HTML)
        if content_type == 'text/markdown':
            #print "Aha, markdown!"
            #print text.value
            html = markdown.markdown(text.value)
            attributes = ['vocab="%s"' % NS.local,
                          'base="%s"'% NS.local,
                          'prefix="%s"' % ' '.join(['%s: %s'% x for x in list(NS.prefixes.items())])]
            if about is not None:
                attributes.append('resource="%s"' % about)
            html = '<div %s>%s</div>' % (' '.join(attributes), html)
            html = Literal(html, datatype=NS.RDF.HTML)
            text = html
            content_type = "text/html"
        #print resource.identifier, content_type
        if html is not None:
            resource.set(NS.sioc.content, html)
            try:
                g.remove((None,None,None))
                g.parse(data=text, format='rdfa', publicID=NS.local)
            except:
                pass
        else:
            #print "Deserializing", g.identifier, 'as', content_type
            #print dataFormats
            if content_type in DATA_FORMATS:
                g.parse(data=text, format=DATA_FORMATS[content_type], publicID=NS.local)
                #print len(g)
            #else:
            #print("not attempting to deserialize.")
#                        try:
#                            sadi.deserialize(g, text, content_type)
#                        except:
#                            pass
#print Graph(store=resource.graph.store).serialize(format="trig")
