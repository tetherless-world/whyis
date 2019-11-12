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

class SETLRAgentTestCase(AgentUnitTestCase):

    def test_basic_file_storage(self):
        self.login_new_user()
        self.dry_run = False
        
        g = ConjunctiveGraph()
        g.parse(data=PERSON_INSTANCE_TRIG, format="trig")
        np = list(self.app.nanopub_manager.prepare(g))[0]
        self.app.nanopub_manager.publish(np)

        print(np.serialize(format='trig').decode('utf8'))
        agent = autonomic.FRIRArchiver()
        results = self.run_agent(agent, nanopublication=np)

        expression = results[0].value(np.identifier, frbr.realization)
        manifestation = results[0].value(expression, frbr.embodiment)
        #fileid = results[0].value(manifestation, whyis.hasFileID)
        #file_handle = self.app.nanopub_depot.get(fileid)
        #data = file_handle.read()
        #digest = hashlib.sha256(data).hexdigest()
        #self.assertEquals(pmanif[digest], manifestation)
        print(np.identifier, len(np), expression, manifestation)
        
        content = self.client.get("/about",query_string={"uri":manifestation},
                                  follow_redirects=True)
        print(content.data.decode('utf8'))
        self.assertEquals(content.mimetype, "application/n-quads")
        digest = hashlib.sha256(content.data).hexdigest()
        print (pmanif[digest])
        print(manifestation)
        self.assertEquals(pmanif[digest], manifestation)
