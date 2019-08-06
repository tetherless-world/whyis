from .test_case import TestCase
from rdflib import URIRef
from flask import Response

class ApiTestCase(TestCase):

    def login_new_user(self, *, email: str = "user@example.com", password: str = "password", role: str = 'Admin') -> Response:
        return self.login(*self.create_user(email, password, role))

    def get_view(self, *, uri: URIRef, mime_type: str, view: str = None, headers: dict = None, expected_template: str = None) -> Response:
        content = self.client.get("/about",
                                  query_string={ a: b for a, b in zip(["uri", "view"], [uri, view]) if b is not None },
                                  headers=headers or {},
                                  follow_redirects=True)
        
        if expected_template is not None:
            self.assertTemplateUsed(expected_template)

        if mime_type is not None:
            self.assertEquals(content.mimetype, mime_type,
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
