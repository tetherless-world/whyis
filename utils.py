import re, threading, traceback, datetime
from rdflib import Literal
import uuid
import hashlib
import base64
import random
from datetime import datetime

def create_id():
    return base64.encodestring(str(random.random()*datetime.now().toordinal()).encode('utf8')).decode('utf8').rstrip('=\n')

def get_max_id(c, graph):
    query = '''select ?id where { ?s a %s ;
               <http://purl.org/dc/terms/identifier> ?id.
               } order by desc(?id) limit 1''' % c.n3()
    i = list(graph.query(query))
    if len(i) == 0:
        return 0
    else:
        result = i[0][0].value
        if result < 1:
            return Literal(0)
        else:
            return Literal(result)
