from typing import Optional, Dict

from .test_case import TestCase
from rdflib import URIRef
from flask import Response

class ApiTestCase(TestCase):

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
