from typing import Optional, Dict

from .test_case import TestCase
from rdflib import URIRef
from flask import Response

class ApiTestCase(TestCase):

    def login_new_user(self, *, email: str = "user@example.com", password: str = "password", role: str = 'Admin') -> Response:
        return self.login(*self.create_user(email, password, role))

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

    def post_nanopub(self, *, data: str, content_type: str, expected_response: int = 201, expected_headers: list = None) -> Response:
        response = self.client.post("/pub",
                                    data=data,
                                    content_type=content_type,
                                    follow_redirects=True)

        self.assertStatus(response, expected_response,
                          "Expected {}, got {} as reponse".format(expected_response, response.status))

        if expected_headers is not None:
            for header in expected_headers:
                self.assertIn(header, response.headers)

        return response

    publish_nanopub = post_nanopub
