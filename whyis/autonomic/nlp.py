from __future__ import division
from past.utils import old_div
import nltk, re, pprint
from whyis import autonomic
from bs4 import BeautifulSoup
from rdflib import *
from slugify import slugify
from whyis import nanopub
from math import log10
import collections

from whyis.namespace import sioc_types, sioc, sio, dc, prov, whyis, text

class HTML2Text(autonomic.UpdateChangeService):
    activity_class = whyis.TextFromHTML

    def getInputClass(self):
        return sioc.Post

    def getOutputClass(self):
        return URIRef("http://purl.org/dc/dcmitype/Text")

    def get_query(self):
        return '''select ?resource where { ?resource <http://rdfs.org/sioc/ns#content> [].}'''

    def process(self, i, o):
        content = i.value(sioc.content)
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text("\n")
        o.add(URIRef("http://schema.org/text"), Literal(text))

class IDFCalculator(autonomic.UpdateChangeService):
    activity_class = whyis.InverseDocumentFrequencyCalculation

    def getInputClass(self):
        return autonomic.whyis.ResolvedText

    def getOutputClass(self):
        return autonomic.whyis.TFIDFText

    @property
    def document_count(self):
        return list(self.app.db.query('''select (count(distinct ?node) as ?count) where {
    ?node sio:hasPart [ prov:specializationOf ?concept; a sio:Term].
}''',
                                       initNs=dict(sio=sio, prov=prov)))[0][0].value

    def process(self, i, o):
        document_count = float(self.document_count)

        query = """select distinct ?concept (count(distinct ?othernode) as ?count) ?assertion where {
  ?node sio:hasPart [ a sio:Term; prov:specializationOf ?concept].
  ?othernode sio:hasPart [ a sio:Term; prov:specializationOf ?concept].
  optional {
    graph ?assertion {
        ?concept sio:InverseDocumentFrequency ?idf.
    }
  }
} group by ?concept ?assertion"""
        for concept, count, assertion in self.app.db.query(query, initBindings=dict(node=i.identifier)):
            idf = log10(old_div(document_count,count.value))
            npub = nanopub.Nanopublication(store=o.graph.store)
            if assertion is not None:
                npub.pubinfo.add((npub.assertion.identifier, prov.wasRevisionOf, assertion))
            npub.assertion.add((concept, sio.InverseDocumentFrequency, Literal(idf)))


class EntityResolver(autonomic.UpdateChangeService):
    activity_class = whyis.EntityResolution

    def getInputClass(self):
        return autonomic.whyis.ExtractedText

    def getOutputClass(self):
        return autonomic.whyis.ResolvedText

    def process(self, i, o):
        #context = ' '.join([term.value(sio.hasValue) for term in i[sio.hasPart]][:20])
        context = ' '.join([term.value(sio.hasValue) for term
                            in sorted(i[sio.hasPart], reverse=True, key=lambda term: term.value(sio.Frequency))[:20]])
        for term in i[sio.hasPart]:
            term_label = term.value(sio.hasValue)
            o_term = o.graph.resource(term.identifier)
            results = self.app.resolve(term, context, label=False)
            if len(results) > 0:
                result = results[0]
            if node is not None:
                #o_term.add(RDFS.label, label)
                o_term.add(autonomic.prov.specializationOf, result['node'])
                o.add(dc.subject, result['node'])

class EntityExtractor(autonomic.UpdateChangeService):
    activity_class = whyis.EntityExtraction

    grammar = r"""
NP: {<DT|PP\$>?<JJ>*<NN>+}   # chunk determiner/possessive, adjectives and noun
    {<NNP>+<NN>*}                # chunk sequences of proper nouns
    }<VBD|IN|DT|PP>+{      # Chink sequences of VBD and IN
"""
    cp = nltk.RegexpParser(grammar)
    property_path = "<http://schema.org/text>|<http://purl.org/dc/terms/summary>|<http://purl.org/dc/terms/abstract>|<http://purl.org/dc/terms/description>|<http://www.w3.org/2000/01/rdf-schema#comment>|<http://www.w3.org/2004/02/skos/core#definition>"

    def __init__(self, property_path=None):
        nltk.download('all', quiet=True)
        if property_path is not None:
            self.property_path = property_path

    def getInputClass(self):
        return URIRef("http://purl.org/dc/dcmitype/Text")

    def getOutputClass(self):
        return autonomic.whyis.ExtractedText

    def get_query(self):
        return '''select ?resource where { ?resource <http://schema.org/text> [].}'''

    def process(self, i, o):
        documents = self.app.db.query('''select ?text where { %s %s ?text.}''' % (i.identifier.n3(), self.property_path))
        tf = self.tf(documents)
        #print tf
        for t, f in list(tf.items()):
            term = o.graph.resource(URIRef(i.identifier+"-term-"+slugify(t)))
            term.add(RDF.type, sio.Term)
            term.add(sio.hasValue, Literal(t))
            #term.add(RDFS.label, Literal(t))
            term.add(sio.Frequency, Literal(f))
            o.add(sio.hasPart, term)

    def tf(self, documents):
        term_vector = collections.defaultdict(float)
        all_mentions = []
        for document, in documents:
            #print document.value
            document = document.value.replace("\n",".\n") # make sure discrete lines become individual sentences.
            document = document.replace("..\n",".\n") # remove the extra periods
            sentences = nltk.sent_tokenize(document)
            sentences = [nltk.word_tokenize(sent) for sent in sentences]
            sentences = [nltk.pos_tag(sent) for sent in sentences]
            sentences = [self.cp.parse(s) for s in sentences]
            nps = [subtree for s in sentences for subtree in s.subtrees() if subtree.label() == "NP"]
            mentions = [re.sub("\.$","",' '.join([word for word, pos in np.leaves()]).lower()) for np in nps]
            all_mentions.extend(mentions)
            for mention in mentions:
                term_vector[mention] += 1
        tf_vector = dict([(mention, old_div(count,len(all_mentions))) for mention, count in list(term_vector.items())])
        return tf_vector
