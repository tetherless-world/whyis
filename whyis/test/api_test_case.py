from .test_case import TestCase


class ApiTestCase(TestCase):

    def publish_nanopub(self, data, content_type, expected_response=201, login=True):
        if login:
            self.login(*self.create_user("user@example.com", "password"))

        response = self.client.post("/pub", data=data,
                                    content_type=content_type,
                                    follow_redirects=True)
        self.assertStatus(response, expected_response,
                          "Expected {}, got {} as reponse".format(expected_response, response))

        return response
        
    def get_view(self, uri, view="view", expected_mime=None, expected_template=None):
        content = self.client.get("/about",
                                query_string={"uri": uri, "view": view},
                                follow_redirects=True)
        
        if expected_template is not None:
            self.assertTemplateUsed(expected_template)

        if expected_mime is not None:
            self.assertEquals(content.mimetype, expected_mime,
                              "Expected {}, got {} as response MIME type".format(expected_mime, content.mimetype))

        return content
