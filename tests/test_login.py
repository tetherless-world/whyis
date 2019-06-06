#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
from testcase import WhyisTestCase

from base64 import b64encode

from rdflib import *

import json
from io import StringIO

class LoginTest(WhyisTestCase):
    
    def test_plain_text_upload(self):
        login_response = self.login(*self.create_user("user@example.com","password"))
        print(login_response.data)
        self.assertNotIn(b'USER = { }', login_response.data)
        #print(login_response.response)

