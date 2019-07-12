import re, threading, traceback, datetime
from rdflib import Literal
import uuid
import hashlib
import base64
import random
from datetime import datetime

def create_id():
    return base64.encodestring(str(random.random()*datetime.now().toordinal()).encode('utf8')).decode('utf8').rstrip('=\n')

def timer(fn):
    def wrapper(*args, **kw):
        start = datetime.datetime.now()
        result = fn(*args, **kw)
        end = datetime.datetime.now()
        print(fn.__name__, "(",args, kw,")", (end-start))
        return result
    return wrapper

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

def print_stacktrace():
    for line in traceback.format_stack()[:-1]:
        print(line.strip())

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

# TODO: There's a risk of the exlusive lock being starved during lots of reads.
class ShLock(object):
    xlock = threading.RLock()
    shlock = threading.Condition()
    lock_count = 0

    def acquire(self,exclusive=True):
        if exclusive:
            self.xlock.acquire()
        else:
            self.shlock.acquire()
            while self.lock_count == 0 and not self.xlock.acquire(False):
                self.shlock.wait()
            self.lock_count += 1
            self.shlock.release()

    def release(self,exclusive=True):
        if exclusive:
            self.xlock.release()
            self.shlock.notify_all()
        else:
            self.shlock.acquire()
            self.lock_count -= 1
            self.shlock.release()
