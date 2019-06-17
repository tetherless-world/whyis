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

def lru(original_function, maxsize=1000):
    mapping = {}

    PREV, NEXT, KEY, VALUE = 0, 1, 2, 3         # link fields
    head = [None, None, None, None]        # oldest
    tail = [head, None, None, None]   # newest
    head[NEXT] = tail

    def fn(*args, **kw):
        key = (args,tuple(kw.items()))
        PREV, NEXT = 0, 1
        #print "Cache lookup for "+str(key)
        link = mapping.get(key, head)
        if link is head:
            #print "Cache miss for "+str(key)
            value = original_function(*args,**kw)
            if len(mapping) >= maxsize:
                old_prev, old_next, old_key, old_value = head[NEXT]
                head[NEXT] = old_next
                old_next[PREV] = head
                del mapping[old_key]
            last = tail[PREV]
            link = [last, tail, key, value]
            mapping[key] = last[NEXT] = tail[PREV] = link
        else:
            #print "Cache hit for "+str(key)
            link_prev, link_next, key, value = link
            link_prev[NEXT] = link_next
            link_next[PREV] = link_prev
            last = tail[PREV]
            last[NEXT] = tail[PREV] = link
            link[PREV] = last
            link[NEXT] = tail
        return value
    return fn

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
