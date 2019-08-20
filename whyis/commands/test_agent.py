# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask


class TestAgent(Command):
    '''Add a nanopublication to the knowledge graph.'''

    def get_options(self):
        return [
            Option('--agent', '-a', dest='agent_path',
                   type=str),
            Option('--dry-run', '-d', action="store_true", dest='dry_run'),
        ]

    def run(self, agent_path, dry_run=False):
        app = flask.current_app
        from pydoc import locate
        agent_class = locate(agent_path)
        agent = agent_class()
        agent.dry_run = dry_run
        if agent.dry_run:
            print("Dry run, not storing agent output.")
        agent.app = app
        print(agent.get_query())
        results = []
        if agent.query_predicate == app.NS.whyis.globalChangeQuery:
            results.extend(agent.process_graph(app.db))
        else:
            for resource in agent.getInstances(app.db):
                for np_uri, in app.db.query('''select ?np where {
    graph ?assertion { ?e ?p ?o.}
    ?np a np:Nanopublication;
        np:hasAssertion ?assertion.
}''', initBindings={'e': resource.identifier}, initNs=app.NS.prefixes):
                    np = app.nanopub_manager.get(np_uri)
                    results.extend(agent.process_graph(np))
        for np in results:
            print(np.serialize(format="trig"))
