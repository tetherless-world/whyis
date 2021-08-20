import collections
import json
import rdflib

from flask import g, request
from functools import reduce
from jinja2 import Environment
from markupsafe import Markup
from slugify import slugify
from urllib import parse

from whyis.namespace import NS

# def geomean(nums):
#    return float(reduce(lambda x, y: x*y, nums))**(1.0/len(nums))

#def composite_z_score(nums):
#    return norm.cdf(sum([norm.ppf(x) for x in nums]))

def configure(app):

    @app.template_filter('urlencode')
    def urlencode_filter(s):
        if isinstance(s, Markup):
            s = s.unescape()
        s = s.encode('utf8')
        s = parse.quote_plus(s)
        return Markup(s)

    @app.template_filter('jsonify')
    def jsonify(o):
        def preprocess(o):
            if isinstance(o, rdflib.Literal):
                return o.value
            elif isinstance(o, list):
                return [preprocess(x) for x in o]
            elif isinstance(o, dict):
                return dict([(key,preprocess(value)) for key, value in o.items()])
            else:
                return o
        return json.dumps(preprocess(o))

    @app.template_filter('labelize')
    def labelize(entry, key='about', label_key='label', fetch=False):
        if key not in entry:
            return None
        resource = None
        try:
            key_uri = rdflib.URIRef(entry[key])
            key_uri.n3()
        except Exception:
            entry[label_key] = entry[key]
            return entry
        if fetch:
            resource = app.get_resource(key_uri)
        else:
            resource = app.Entity(app.db, key_uri)
        entry[label_key] = app.get_label(resource.description())
        return entry

    @app.template_filter('iter_labelize')
    def iter_labelize(entries, *args, **kw):
        for entry in entries:
            labelize(entry, *args, **kw)
        return entries

    app.labelize = labelize

    @app.template_filter('map_list')
    def map_list(entries, source, destination, fn, **kw):
        for entry in entries:
            entry[destination] = fn(entry[source], **kw)
        return entries

    @app.template_filter('lang')
    def lang_filter(terms):
        terms = list(terms)
        if terms is None or not terms:
            return []
        resources = [x for x in terms if not isinstance(x, rdflib.Literal)]
        literals = [x for x in terms if isinstance(x, rdflib.Literal)]
        languages = { x.language for x in literals if x.language is not None }
        best_lang = request.accept_languages.best_match(list(languages))
        best_terms = [x for x in literals if x.language == best_lang]
        if not best_terms:
            best_terms = [x for x in literals if x.language == app.config['default_language']]
        if best_terms:
            return resources + best_terms
        return resources
    app.lang_filter = lang_filter

    @app.template_filter('query')
    def query_filter(query, graph=app.db, prefixes=None, values=None):
        if prefixes is None: # default arguments are evaluated once, ever
            prefixes = {}

        namespaces = dict(app.NS.prefixes)
        namespaces.update({ key: rdflib.URIRef(value) for key, value in list(prefixes.items())})
        params = { 'initNs': namespaces}
        if values is not None:
            params['initBindings'] = values
        return [x.asdict() for x in graph.query(query, **params)]


    @app.template_filter("fromjson")
    def fromjson(json_text):
        return json.loads(json_text)

    @app.template_filter('construct')
    def construct_filter(query, graph=app.db, prefixes=None, values=None):
        if prefixes is None:
            prefixes = {}

        def remap_bnode(x):
            if isinstance(x, rdflib.URIRef) and x.startswith('bnode:'):
                return rdflib.BNode(x.replace('bnode:',''))
            return x
        namespaces = dict(app.NS.prefixes)
        namespaces.update({ key: rdflib.URIRef(value) for key, value in prefixes.items() })
        params = { 'initNs': namespaces}
        if values is not None:
            params['initBindings'] = values
        conjunctive_graph = rdflib.graph.ConjunctiveGraph()
        for stmt in graph.query(query, **params):
            conjunctive_graph.add(tuple([remap_bnode(x) for x in stmt]))
        return conjunctive_graph

    @app.template_filter('serialize')
    def serialize_filter(graph, **kwargs):
        return graph.serialize(**kwargs).decode()

    @app.template_filter('attributes')
    def attributes(query, this):
        result = {
            "@id" : this.identifier,
            'description' : [labelize({'@id':property, "value": value},key="@id") for property, value in app.get_summary(this)],
            'type' : [labelize({"@id":x.identifier},key='@id') for x in this.description()[app.NS.RDF.type]],
            "attributes" : collections.defaultdict(lambda : dict(values=[]))
        }
        result['description'] = sorted(result['description'], key=lambda x: len(x['value']))
        thumbnail = this.description().value(app.NS.foaf.depiction)
        if thumbnail is not None:
            result['thumbnail'] = thumbnail.identifier
        labelize(result, key="@id")
        attrs = query_filter(query, values=dict(this=this.identifier))
        for attr in attrs:
            result['attributes'][attr['property']]['@id'] = attr['property']
            result['attributes'][attr['property']]['values'].append(attr)
        for attr in list(result['attributes'].values()):
            values = set(lang_filter([x['value'] for x in attr['values'] if x['value'] != result['label']]))
            attr['values'] = [x for x in attr['values'] if x['value'] in values]
            labelize(attr, key='@id')
            for value in attr['values']:
                if isinstance(value['value'], rdflib.URIRef):
                    value['@id'] = value['value']
                    labelize(value, key='@id', label_key='value')
                if 'unit' in value:
                    labelize(value, key='unit', label_key='unit_label')
                del value['property']
        result['attributes'] = [x for x in list(result['attributes'].values()) if len(x['values']) > 0]
        return result

    @app.template_filter('include')
    def include(entity, view='view', **kwargs):
        if not isinstance(entity, app.Entity):
            entity = app.get_resource(entity)
        if not kwargs:
            kwargs = None

        return app.render_view(entity, view=view, args=kwargs)[0]

    @app.template_filter('probquery')
    def probquery(select):
        return '''select distinct
?source
?link
?target
?link_type
#(group_concat(distinct ?link_type; separator=" ") as ?link_types)
?np
?probability
#(max(?tfidf) as ?tfidf)
(max(?frequency) as ?frequency)
(max(?idf) as ?idf)
(group_concat(distinct ?article; separator=" ") as ?articles)
where {
    hint:Query hint:optimizer "Runtime" .

    %s

    ?assertion a np:Assertion.
    ?np np:hasAssertion ?assertion.
    optional {
      ?np np:hasProvenance ?provenance
      graph ?provenance {
        ?assertion prov:wasDerivedFrom|dc:references ?article.
        #?article a sio:PeerReviewedArticle.
      }
      optional {
        ?article sio:hasAttribute [ a whyis:ConfidenceScore; sio:hasValue ?probability].
      }
      minus { ?article a np:Nanopublication.}
    }
    optional {
      graph ?prob_assertion {
        ?assertion sio:hasAttribute [ a sio:ProbabilityMeasure; sio:hasValue ?probability].
      }
      ?prob_np np:hasAssertion ?prob_assertion.
    }
    optional {
      ?source sio:hasPart ?term.
      ?term prov:specializationOf ?target;
            sio:Frequency ?frequency.
      optional {
        ?target sio:InverseDocumentFrequency ?idf.
      }
      #bind (?frequency * ?idf as ?tfidf)
      #bind (?tfidf/(1+?tfidf) as ?probability)
    }
} group by ?source ?target ?link ?link_type ?np ?prob_np ?probability''' % select

    @app.template_filter('mergeLinks')
    def mergeLink(edges):
        from scipy.stats import combine_pvalues

        base_rate = app.config['base_rate_probability']

        def merge(links):
            result = dict(links[0])
            result['from'] = []
            result['articles'] = []
            for i in links:
                if 'probability' not in i:

                    # Do a very rudimentary meta-analysis based on the number of supporting papers
                    rates = [base_rate for x in i['articles']]
                    if not rates:
                        rates = [base_rate]
                    p = combine_pvalues(rates, method="stouffer")[1]
                    i['probability'] = p
                    if 'frequency' in i:
                        idf = 10 ** i.get('idf', rdflib.Literal(100)).value
                        tfidf = (0.5+i['frequency'].value) * idf

                        # old_div is no longer defined!
                        i['probability'] = combine_pvalues([tfidf/(1+tfidf)],method='stouffer')[1]
                else:
                    i['probability'] = i['probability'].value
                result['from'].append(i['np'])
                result['articles'].extend(i['articles'])
            result['probability'] = max([i['probability'] for i in links])
            #print "end: "
            return result

        byLink = collections.defaultdict(list)
        for edge in edges:
#            edge['source_types'] = [x for x in edge.get('source_types','').split(' ') if len(x) > 0]
#            edge['target_types'] = [x for x in edge.get('target_types','').split(' ') if len(x) > 0]
            edge['link_types'] = [x for x in edge.get('link_type','').split(' ') if len(x) > 0]
            edge['articles'] = [x for x in edge.get('articles','').split(' ') if len(x) > 0]
            byLink[(edge['source'],edge['link'],edge['target'])].append(edge)
        result = list(map(merge, list(byLink.values())))
        return result

    @app.template_filter('mergeLinkTypes')
    def mergeLinkTypes(edges):
        from scipy.stats import combine_pvalues

        def merge(links):
            result = dict(links[0])
            result['from'] = []
            result['articles'] = []
            del result['np']
            for i in links:
                result['from'].extend(i['from'])
                result['articles'].extend(i['articles'])
            result['probability'] = combine_pvalues([e['probability'] for e in links], method="stouffer")[1]
            if result['probability'] < 1 and result['probability'] > 0:
                from scipy.stats import norm
                result['zscore'] = norm.ppf(result['probability'])
            return result

        result = collections.defaultdict(list)
        for edge in edges:
        #print edge
            #for link_type in edge['link_types']:
            result[(edge['source'],tuple(sorted(edge['link_types'])),edge['target'])].append(edge)
        result = list(map(merge, list(result.values())))
        return result

    def types(x):
        return

    @app.template_filter('probit')
    def probit(q, **values):
        q = probquery(q)
        results = query_filter(q, values=values)
        results = mergeLink(results)
        results = sorted(mergeLinkTypes(results), key=lambda x: x['probability'], reverse=True)
        for r in results:
            if 'link_type' in r:
                labelize(r, 'link_type', 'link_label')
            r['link_types'] = [labelize({"uri":x},'uri','label') for x in r['link_types']]
            # resource = # return value of the next line is never used
            app.get_resource(rdflib.URIRef(r['link']))
            labelize(r, 'link','label')
            #r['descriptions'] = [v for k,v in app.get_summary(resource)]
        if 'target' not in values:
            results = iter_labelize(results,'target','target_label')
            for r in results:
                r['target_types'] = [x for x in app.db.query('select ?t where {?x a ?t}',
                                                             initBindings=dict(x=r['target']))]
        if 'source' not in values:
            results = iter_labelize(results,'source','source_label')
            for r in results:
                r['source_types'] = [x for x in app.db.query('select ?t where {?x a ?t}',
                                                             initBindings=dict(x=r['source']))]
        return results

    env = Environment()
    facet_value_template = env.from_string('''
SELECT DISTINCT (1 as ?count) ?value ?unit ?indep_value ?indep_unit
WHERE {
  SELECT DISTINCT ?value ?unit ?indep_value ?indep_unit {
    {
      SELECT DISTINCT ?value ?unit ?indep_value ?indep_unit {
        ?id rdf:type/rdfs:subClassOf* <{{facet['class']}}> .
        FILTER (!ISBLANK(?id))
        FILTER ( !strstarts(str(?id), "bnode:") )
        {% if facet['typeProperty']|length %}
        ?id {{facet['predicate']}} ?value_object.
        ?value_object {{facet['typeProperty']}} ?value.
        {% if 'unitPredicate' in facet %}optional { ?value_object {{facet['unitPredicate']}} ?unit. }{%endif%}
        {% if 'independentVariables' in facet %}optional {
          ?value_object {{facet['independentVariables']}} ?indep.
          ?indep {{facet['typeProperty']}} ?indep_value.
          {% if 'unitPredicate' in facet %}optional {
            ?indep {{facet['unitPredicate']}} ?indep_unit.
          }{%endif%}
        }{%endif%}
        {% else %}
        ?id {{facet['predicate']}} ?value.
        {% endif %}
        {{facet['specifier']}}

    {% for constraint in constraints %}{{constraint}}{% endfor %}

    {% for variable in variables %}
    {% if 'valuePredicate' in variable %}
      ?id {{variable['predicate']}} [
        {{variable['typeProperty']}} <{{variable['value']}}>;
        {{variable['valuePredicate']}} ?{{variable['field']}};
        {% if 'unit' in variable %}
          {{variable['unitPredicate']}} <{{variable['unit']}}>;
        {% endif %}
      ].
    {% else %}
      ?id {{variable['predicate']}} [
        {{variable['typeProperty']}} ?{{variable['field']}};
      ].
    {% endif %}
  {% endfor %}

      } GROUP BY ?value ?unit ?indep_value ?indep_unit
    }
    FILTER(BOUND(?value))
  }
}''')

    @app.template_filter('facet_values')
    def facet_values(facets, variables, constraints):
        if constraints:
            constraints = json.loads(constraints)
        if variables:
            variables = json.loads(variables)
            var_map = { v['field']: v for v in variables}
            variables = list(var_map.values())
        results = []
        allowed_property_types = set([
        'http://www.w3.org/2002/07/owl#ObjectProperty',
        'http://www.w3.org/2002/07/owl#DatatypeProperty'
        ])
        for facet in facets:
            facet['type'] = 'nominal'
            if facet['propertyType'] not in allowed_property_types:
                continue
            if 'predicate' not in facet and 'property' in facet:
                facet['predicate'] = '<'+facet['property']+'>'
            if 'typeProperty' not in facet and facet['propertyType'] == 'http://www.w3.org/2002/07/owl#ObjectProperty':
                facet['typeProperty'] = 'a'
            if True:#'valuePredicate' in facet:
                query = facet_value_template.render(facet=facet, variables=variables, constraints=constraints)
                print(query)
                values = {}
                for value in query_filter(query):
                    if (value['value'],value.get('unit',None)) not in values:
                        val = {
                          'value' : value['value'],
                          'count' : value['count'],
                          'indep_vals' : []
                        }
                        values[(value['value'],value.get('unit',None))] = val
                        if 'unit' in value:
                            val['unit'] = value['unit']
                    val = values[(value['value'],value.get('unit',None))]
                    if 'indep_value' in value:
                        v = { 'value' : value['indep_value'] }
                        if 'indep_unit' in value:
                            v['unit'] = value['indep_unit']
                        val['indep_vals'].append(v)
                if 'valuePredicate' not in facet:
                    f = dict(facet)
                    f['field'] = f['facetId']
                    f['name'] = f['label']
                    f['unit_label'] = 'All'
                    results.append(f)
                for value in values.values():
                    value.update(facet)
                    fieldName = [value['facetId'],
                                 slugify(value['value'],separator='_',lowercase=False)]
                    if 'unit' in value:
                        fieldName.append(slugify(value['unit'],separator='_',lowercase=False))
                    value['type'] = 'quantitative'
                    fieldName = '__'.join(fieldName)
                    value['field'] = fieldName
                    for indep_value in value['indep_vals']:
                        indepFieldName = [
                            fieldName,
                            slugify(indep_value['value'],separator='_',lowercase=False)
                        ]
                        if 'unit' in indep_value:
                            indepFieldName.append(slugify(indep_value['unit'],separator='_',lowercase=False))
                        indep_value['type'] = 'quantitative'
                        indepFieldName = '__'.join(indepFieldName)
                        indep_value['field'] = indepFieldName
                    iter_labelize(value['indep_vals'], key='value', label_key='name')
                    iter_labelize(value['indep_vals'], key='unit', label_key='unit_label')
                    results.append(value)
            else:
                facet['field'] = facet['facetId']
                facet['name'] = facet['label']
                results.append(facet)
        iter_labelize(results, key='value', label_key='name')
        iter_labelize(results, key='unit', label_key='unit_label')
        for result in results:
            if 'value' in result:
                result['value'] = result['value'].n3()
        return results

    instance_data_template = env.from_string('''SELECT DISTINCT
?id
{%- for facet, vars in variables | groupby('facetId') %}
  {%- if vars[0]['multiType'] == 'union' %}
    (GROUP_CONCAT(?{{facet}}; separator=', ') AS ?{{facet}})
  {%- else  %}
  {%- for variable in vars %}
    ?{{variable['field']}}
    {%- for indep_variable in variable['indep_vals'] %}
    ?{{indep_variable['field']}}
    {%- endfor %}
  {%- endfor %}
  {% endif %}
{%- endfor %}
WHERE {
    ?id rdf:type {{this.identifier.n3()}}.
    {%- for variable in variables %}
    {%- if variable.selectionType == 'Show' %}
    optional {
    {%- endif %}
    {%- if 'valuePredicate' in variable %}
      ?id {{variable['predicate']}} ?{{variable['field']}}_.

      ?{{variable['field']}}_ {{variable['typeProperty']}} {{variable['value']}};
        {{variable['valuePredicate']}} ?{{variable['field']}};
        {%- if 'unit' in variable %}
          {{variable['unitPredicate']}} <{{variable['unit']}}>;
        {%- endif %}
      .

    {%- for indep_variable in variable['indep_vals'] %}
        optional {
          ?{{variable['field']}}_ {{variable['independentVariables']}} [
            {{variable['typeProperty']}} <{{indep_variable['value']}}>;
            {{variable['valuePredicate']}} ?{{indep_variable['field']}};
            {%- if 'unit' in indep_variable %}
              {{variable['unitPredicate']}} <{{indep_variable['unit']}}>;
            {%- endif %}
          ].
        }
        {%- endfor %}
    {%- elif variable['multiType'] != 'union'%}
        ?id {{variable['predicate']}} ?{{variable['field']}}_.
        {{variable['specifier'].replace('?value', '?'+variable['field']+"_")}}
        ?{{variable['field']}}_ rdfs:label ?{{variable['field']}}.
        {%- if 'value' in variable %}
            {{variable['specifier'].replace('?value', variable['value'])}}
            {{'?'+variable['field']+"_"}} rdf:type/rdfs:subClassOf* {{variable['value']}}.
        {%- endif %}
    {%- endif %}
    {%- if variable.selectionType == 'Show' %}} {% endif %}
  {%- endfor %}
  {%- for facet, vars in variables | groupby('facetId') %}
    {%- if vars[0]['multiType'] == 'union' %}
        {%- for variable in vars %}
        {
            ?id {{variable['predicate']}} ?{{variable['field']}}_.
            {{variable['specifier'].replace('?value', '?'+facet+'_')}}
            ?{{facet}}_ rdfs:label ?{{facet}}.
            {%- if 'value' in variable %}
                {{variable['specifier'].replace('?value', variable['value'])}}
                ?{{facet}}_ rdfs:subClassOf* {{variable['value']}}.
            {%- endif %}
        }{% if not loop.last %} UNION {% endif %}
        {%- endfor %}
    {%- endif %}
  {%- endfor %}
}
GROUP BY ?id 
{%- for variable in variables %}
  {%- if variable['multiType'] != 'union' %}
    ?{{variable['field']}}
    {%- for indep_variable in variable['indep_vals'] %}
      ?{{indep_variable['field']}}
    {%- endfor %}
  {%- endif %}
{%- endfor %}
''')
    @app.template_filter('instance_data')
    def instance_data(this, variables, constraints):
        if constraints:
            constraints = json.loads(constraints)
        else:
            constraints = []
        if variables:
            variables = json.loads(variables)
        else:
            variables = []
        query = instance_data_template.render(constraints=constraints, variables=variables, this=this)
        print(query)
        return query

    @app.template_filter('get_views_list')
    def get_views_list(this):
        types = []
        types.extend((x, 1) for x in app.vocab[this.identifier : NS.RDF.type])
        if not types: # KG types cannot override vocab types. This should keep views stable where critical.
            types.extend([(x.identifier, 1) for x in this.description()[NS.RDF.type]  if isinstance(x, rdflib.URIRef)])
        #if len(types) == 0:
        types.append([NS.RDFS.Resource, 100])
        type_string = ' '.join(["(%s %d)" % (x.n3(), i) for x, i in types])
        view_query = '''select ?navlist (count(?mid)+?priority as ?rank) where {
    ?c rdfs:subClassOf* ?mid.
    ?mid rdfs:subClassOf* ?class.
    ?class whyis:hasNavigation ?navlist.
} group by ?c ?class order by ?rank limit 1
values (?c ?priority) { %s }
''' % type_string
        views = list(app.vocab.query(view_query, initNs=dict(whyis=NS.whyis, dc=NS.dc)))
        if len(views) == 0:
            return []
        nav = list(app.vocab.collection(views[0][0]))
        nav = [{'property': x,
                'view': app.vocab.value(x, NS.dc.identifier),
                'label':app.get_label(app.vocab.resource(x))}
               for x in nav]
        return nav
