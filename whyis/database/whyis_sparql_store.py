# -*- coding:utf-8 -*-

from rdflib.plugins.stores.sparqlstore import SPARQLStore


class WhyisSPARQLStore(SPARQLStore):
    
    def _inject_prefixes(self, query, extra_bindings):
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])
