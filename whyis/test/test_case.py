import flask_testing

from flask import current_app
from flask import Response
from rdflib import URIRef
from typing import Optional, Dict
from depot.manager import DepotManager

class TestCase(flask_testing.TestCase):

    def login_new_user(self, *, email: str = "user@example.com", password: str = "password", username: str = "identifier", role: str = 'Admin') -> Response:
        return self.login(*self.create_user(email=email, password=password, username=username, roles=role))

    def get_view(self, *, uri: URIRef, mime_type: str, view: Optional[str] = None, headers = None, expected_template: Optional[str] = None, query_string: Optional[Dict[str, str]]=None) -> Response:
        query_string = query_string.copy() if query_string is not None else {}
        query_string["uri"] = uri
        if view is not None:
            query_string["view"] = view

        content = self.client.get("/about",
                                  query_string=query_string,
                                  headers=headers or {},
                                  follow_redirects=True)

        if expected_template is not None:
            self.assertTemplateUsed(expected_template)

        if mime_type is not None:
            self.assertEqual(content.mimetype, mime_type,
                              "Expected {}, got {} as response MIME type".format(mime_type, content.mimetype))

        return content


    def create_app(self):
        from whyis.config.default import Test

        if 'ADMIN_ENDPOINT' in Test:
            del Test['ADMIN_ENDPOINT']
            del Test['KNOWLEDGE_ENDPOINT']
        Test['TESTING'] = True
        Test['WTF_CSRF_ENABLED'] = False
        Test['NANOPUB_ARCHIVE'] = {
            'depot.backend' : 'depot.io.memory.MemoryFileStorage'
        }
        Test['DEFAULT_ANONYMOUS_READ'] = False
        Test['FILE_ARCHIVE'] = {
            'depot.backend' : 'depot.io.memory.MemoryFileStorage'
        }
        # Default port is 5000
        Test['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        Test['LIVESERVER_TIMEOUT'] = 10

        from whyis.app_factory import app_factory
        application = app_factory(config.Test, config.project_name)

        return application

    def create_user(self, email, password, username="identifier", fn="First", ln="Last", roles='Admin'):
        from whyis import commands
        from uuid import uuid4
        pw = 'password'
        creator = commands.CreateUser()
        creator.run(email, password, fn, ln, username, roles)
        return email, password

    def login(self, email, password):
        return self.client.post('/login', data={'email': email, 'password': password, 'remember': 'y'},
                                follow_redirects=True)
