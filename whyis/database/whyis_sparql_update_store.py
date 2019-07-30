# -*- coding:utf-8 -*-

from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib.plugins.stores.sparqlconnector import SPARQLConnectorException, _response_mime_types


class WhyisSPARQLUpdateStore(SPARQLUpdateStore):
    # To resolve linter warning
    # "attribute defined outside  __init__"
    def __init__(self, *args, **kwargs):
        self.publish = None
        SPARQLUpdateStore.__init__(self, *args, **kwargs)

    def _inject_prefixes(self, query, extra_bindings):
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])

    def _update(self, update):
        self._updates += 1
        
        if not self.update_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {}

        headers = {
            'Accept': _response_mime_types[self.returnFormat],
            'Content-type': 'application/sparql-update'
        }

        args = dict(self.kwargs)

        args.update(url=self.update_endpoint,
                    data=update.encode('utf-8'))

        # merge params/headers dicts
        args.setdefault('params', {})
        args['params'].update(params)
        args.setdefault('headers', {})
        args['headers'].update(headers)

        res = self.session.post(**args)

        res.raise_for_status()
