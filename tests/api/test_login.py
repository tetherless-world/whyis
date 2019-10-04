from base64 import b64encode

from rdflib import *

from flask_security.confirmable import requires_confirmation
from flask_security.utils import  hash_password, localize_callback, url_for_security, validate_redirect_url

from flask_security.core import current_user
from flask_login import login_user

import json
from io import StringIO

from whyis.test.api_test_case import ApiTestCase


class TestLogin(ApiTestCase):
    def test_direct_login(self):
        user_details = self.create_user("user@example.com","password")
        self.assertEquals(user_details[0], 'user@example.com')
        user_obj = self.app.datastore.get_user('user@example.com')
        self.assertNotEquals(user_obj, None)
        self.assertEquals('user@example.com', user_obj.email)

        
        self.assertNotEquals(None, user_obj.password)
        self.assertTrue(user_obj.verify_and_update_password("password"))
        self.assertFalse(requires_confirmation(user_obj))
        self.assertTrue(user_obj.is_active)

        login_user(user_obj)
       
        #login_response = self.login(*user_details)
        self.assertTrue(current_user.is_authenticated)
        #self.assertNotIn(b'USER = { }', login_response.data)
        #print(login_response.response)

    def test_web_login(self):
        user_details = self.create_user("user@example.com","password")
        self.assertEquals(user_details[0], 'user@example.com')
        user_obj = self.app.datastore.get_user('user@example.com')
        self.assertNotEquals(user_obj, None)
        self.assertEquals('user@example.com', user_obj.email)

        
        self.assertNotEquals(None, user_obj.password)
        self.assertTrue(user_obj.verify_and_update_password("password"))
        self.assertFalse(requires_confirmation(user_obj))
        self.assertTrue(user_obj.is_active)
       
        login_response = self.login(*user_details)
        #self.assertTrue(current_user.is_authenticated)
        self.assertNotIn(b'USER = { }', login_response.data)
        #print(login_response.response)

