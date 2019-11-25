import os
from base64 import b64encode

from rdflib import *

import json
from io import StringIO

from whyis import nanopub
from whyis.namespace import *

from whyis import autonomic
from whyis.test.agent_unit_test_case import AgentUnitTestCase
from tests.api.api_test_data import PERSON_INSTANCE_TRIG
import hashlib

pmanif = Namespace('tag:tw.rpi.edu,2011:manifestation_sha256-')

class FRIRAgentTestCase(AgentUnitTestCase):

    def test_basic_file_storage(self):
        self.login_new_user()
        self.dry_run = False
        
        g = ConjunctiveGraph()
        g.parse(data=PERSON_INSTANCE_TRIG, format="trig")
        np = list(self.app.nanopub_manager.prepare(g))[0]
        self.app.nanopub_manager.publish(np)

        agent = autonomic.FRIRArchiver()
        results = self.run_agent(agent, nanopublication=np)

        expression = results[0].value(np.identifier, frbr.realization)
        manifestation = results[0].value(expression, frbr.embodiment)
        
        content = self.client.get("/about",query_string={"uri":manifestation},
                                  follow_redirects=True)
        # This isn't going to work until we untangle the app
        # configured by manage.py from the app that's configured for
        # running the tests. The get_entity blueprint seems to be
        # using the manage.py app.
        
        self.assertEquals(content.mimetype, "application/n-quads")
        digest = hashlib.sha256(content.data).hexdigest().lstrip('0')
        self.assertEquals(pmanif[digest], manifestation)

    def test_archive_deletion(self):
        self.login_new_user()
        self.dry_run = False
        
        g = ConjunctiveGraph()
        g.parse(data=PERSON_INSTANCE_TRIG, format="trig")
        np = list(self.app.nanopub_manager.prepare(g))[0]
        self.app.nanopub_manager.publish(np)

        agent = autonomic.FRIRArchiver()
        results = self.run_agent(agent, nanopublication=np)

        expression = results[0].value(np.identifier, frbr.realization)
        manifestation = results[0].value(expression, frbr.embodiment)
        fileid = results[0].value(manifestation, whyis.hasFileID)
        
        self.app.nanopub_manager.retire(np.identifier)
        self.assertFalse(self.app.nanopub_depot.exists(fileid))
        
    def test_no_self_archive(self):
        self.login_new_user()
        self.dry_run = False
        
        g = ConjunctiveGraph()
        g.parse(data=PERSON_INSTANCE_TRIG, format="trig")
        np = list(self.app.nanopub_manager.prepare(g))[0]
        self.app.nanopub_manager.publish(np)

        agent = autonomic.FRIRArchiver()
        results = self.run_agent(agent, nanopublication=np)

        second_results = self.run_agent(agent,nanopublication=results[0])
        self.assertEquals(len(second_results),0)
        
