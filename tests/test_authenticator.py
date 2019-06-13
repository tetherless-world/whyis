from testcase import WhyisTestCase
from authenticator import *

class AuthenticatorTest(WhyisTestCase):

  key = "" # TODO implement

  def test_api_key(self):
    auth = APIKeyAuthenticator(self.key)
    # auth.authenticate(request, datastore, config)
    # assert something

  def test_jwt(self):
    auth = JWTAuthenticator(self.key)
    # auth.authenticate(request, datastore, config)
    # assert something
