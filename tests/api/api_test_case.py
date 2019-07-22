#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
import urllib.request, urllib.error, urllib.parse
from flask import Flask, g
from flask_testing import TestCase
from flask_login import login_user, current_user, current_app
import requests

from whyis_test_case import WhyisTestCase


class ApiTestCase(WhyisTestCase):
    pass
