from flask_ld.utils import lru

import urllib
from markupsafe import Markup

from flask import g, request
import rdflib
from rdflib import *

import math
import collections

from scipy.stats import norm

from scipy.stats import combine_pvalues

def geomean(nums):
    return float(reduce(lambda x, y: x*y, nums))**(1.0/len(nums))

#def composite_z_score(nums):
#    return norm.cdf(sum([norm.ppf(x) for x in nums]))

def configure(app):
    
    @app.template_filter('urlencode')
    def urlencode_filter(s):
        if type(s) == 'Markup':
            s = s.unescape()
        s = s.encode('utf8')
        s = urllib.quote_plus(s)
        return Markup(s)

    @app.template_filter('labelize')
    def labelize(entry, key='about', label_key='label', fetch=False):
        resource = None
        if fetch:
            resource = app.get_resource(URIRef(entry[key]))
        else:
            resource = app.Entity(app.db, URIRef(entry[key]))
        entry[label_key] = g.get_label(resource.description())
        return entry

    @app.template_filter('iter_labelize')
    def iter_labelize(entries, *kw):
        for entry in entries:
            labelize(entry, *kw)
        return entries

    app.labelize = labelize
        
    @app.template_filter('lang')
    def lang_filter(terms):
        terms = list(terms)
        if terms is None or len(terms) == 0:
            return []
        resources = [x for x in terms if not isinstance(x, rdflib.Literal)]
        literals = [x for x in terms if isinstance(x, rdflib.Literal)]
        languages = set([x.language for x in literals if x.language is not None])
        best_lang = request.accept_languages.best_match(list(languages))
        best_terms = [x for x in literals if x.language == best_lang]
        if len(best_terms) == 0:
            best_terms = [x for x in literals if x.language == app.config['default_language']]
        if len(best_terms) > 0:
            return resources + best_terms
        return resources
    app.lang_filter = lang_filter

    @app.template_filter('query')
    def query_filter(query, graph=app.db, prefixes={}, values=None):
        namespaces = dict(app.NS.prefixes)
        namespaces.update(dict([(key, rdflib.URIRef(value)) for key, value in prefixes.items()]))
        params = { 'initNs': namespaces}
        if values is not None:
            params['initBindings'] = values
        return [x.asdict() for x in graph.query(query, **params)]

    @app.template_filter('probquery')
    def probquery(select):
        return '''select distinct 
?source 
?link
?target
(group_concat(distinct ?link_type; separator=" ") as ?link_types) 
?np 
?probability 
?prob_np
(group_concat(distinct ?article; separator=" ") as ?articles) 
where {
    hint:Query hint:optimizer "Runtime" .

    %s
    
    ?assertion a np:Assertion.
    ?np np:hasAssertion ?assertion.
    optional {
      ?np np:hasProvenance ?provenance
      graph ?provenance {
        ?assertion prov:wasDerivedFrom ?article.
        ?article a sio:PeerReviewedArticle.
      }
    }
    optional {
      graph ?prob_assertion {
        ?assertion sio:hasAttribute [ a prov:ProbabilityMeasure; sio:hasValue ?probability].
      }
      ?prob_np np:hasAssertion ?prob_assertion.
    }
} group by ?source ?target ?link ?np ?probability ?prob_np''' % select

    @app.template_filter('mergeLinks')
    def mergeLink(edges):
        base_rate = app.config['base_rate_probability']
        def merge(links):
            result = dict(links[0])
            result['from'] = []
            result['articles'] = []
            for i in links:
                if 'probability' not in i:
                    # Do a very rudimentary meta-analysis based on the number of supporting papers
                    rates = [base_rate for x in i['articles']]
                    if len(rates) == 0:
                        rates = [base_rate]
                    p = combine_pvalues(rates, method="stouffer")[1]
                    i['probability'] = p
                result['from'].append(i['np'])
                result['articles'].extend(i['articles'])
            result['probability'] = geomean([i['probability'] for i in links])
            #print "end: "
            return result
    
        byLink = collections.defaultdict(list)
        for edge in edges:
#            edge['source_types'] = [x for x in edge.get('source_types','').split(' ') if len(x) > 0]
#            edge['target_types'] = [x for x in edge.get('target_types','').split(' ') if len(x) > 0]
            edge['link_types'] = [x for x in edge.get('link_types','').split(' ') if len(x) > 0]
            edge['articles'] = [x for x in edge.get('articles','').split(' ') if len(x) > 0]
            byLink[(edge['source'],edge['link'],edge['target'])].append(edge)
        result = map(merge, byLink.values())
        return result

    @app.template_filter('mergeLinkTypes')
    def mergeLinkTypes(edges):
        def merge(links):
            result = dict(links[0])
            result['from'] = []
            result['articles'] = []
            del result['np']
            for i in links:
                result['from'].extend(i['from'])
                result['articles'].extend(i['articles'])
            result['probability'] = combine_pvalues([e['probability'] for e in links], method="stouffer")[1]
            result['zscore'] = norm.ppf(result['probability'])
            return result
        
        result = collections.defaultdict(list)
        for edge in edges:
        #print edge
            #for link_type in edge['link_types']:
            result[(edge['source'],tuple(sorted(edge['link_types'])),edge['target'])].append(edge)
        result = map(merge, result.values())
        return result

    def types(x):
        return 
    
    @app.template_filter('probit')
    def probit(q, **values):
        q = probquery(q)
        print q
        results = query_filter(q, values=values)
        results = mergeLink(results)
        results = mergeLinkTypes(results)
        if 'target' not in values:
            results = iter_labelize(results,'target','target_label')
            for r in results:
                r['target_types'] = [x for x, in app.db.query('select ?t where {?x a ?t}',initBindings=dict(x=r['target']))]
        if 'source' not in values:
            results = iter_labelize(results,'source','source_label')
            for r in results:
                r['source_types'] = [x for x, in app.db.query('select ?t where {?x a ?t}',initBindings=dict(x=r['source']))]
        return results
