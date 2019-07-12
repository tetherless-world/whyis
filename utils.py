import re, threading, traceback, datetime
from rdflib import Literal
import uuid
import hashlib
import base64
import random
from datetime import datetime

def create_id():
    return base64.encodestring(str(random.random()*datetime.now().toordinal()).encode('utf8')).decode('utf8').rstrip('=\n')
