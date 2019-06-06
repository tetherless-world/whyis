#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
import urllib.request, urllib.error, urllib.parse
from flask import Flask, g
from flask_testing import TestCase
from flask_login import login_user, current_user, current_app
import requests

class WhyisTestCase(TestCase):
    
    def create_app(self):
        from main import app_factory
        from depot.manager import DepotManager
        import config_defaults

        if 'admin_queryEndpoint' in config_defaults.Test:
            del config_defaults.Test['admin_queryEndpoint']
            del config_defaults.Test['admin_updateEndpoint']
            del config_defaults.Test['knowledge_queryEndpoint']
            del config_defaults.Test['knowledge_updateEndpoint']

        # Default port is 5000
        config_defaults.Test['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        config_defaults.Test['LIVESERVER_TIMEOUT'] = 10

        application = app_factory(config_defaults.Test, config_defaults.project_name)
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False

        return application

    def create_user(self, email, password, username="identifier", fn="First", ln="Last", roles='admin'):
        import commands
        from uuid import uuid4
        pw = 'password'
        creator = commands.CreateUser()
        creator.run(email, password, fn, ln, username, roles)
        return email, password

    def login(self, email, password):
        return self.client.post('/login', data={ 'email': email, 'password': password, 'remember':'y' }, follow_redirects=True)

    def run_agent(self, agent, nanopublication=None):
        app = self.app
        agent.dry_run = True
        agent.app = app
        results = []
        if nanopublication is not None:
            results.extend(agent.process_graph(nanopublication))
        elif agent.query_predicate == app.NS.whyis.globalChangeQuery:
            results.extend(agent.process_graph(app.db))
        else:
            print("Running as update agent")
            for resource in agent.getInstances(app.db):
                print(resource.identifier)
                for np_uri, in app.db.query('''select ?np where {
    graph ?assertion { ?e ?p ?o.}
    ?np a np:Nanopublication;
        np:hasAssertion ?assertion.
}''', initBindings={'e': resource.identifier}, initNs=app.NS.prefixes):
                    print(np_uri)
                    np = app.nanopub_manager.get(np_uri)
                    results.extend(agent.process_graph(np))
        return results
