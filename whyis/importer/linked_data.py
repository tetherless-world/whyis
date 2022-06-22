import requests
import rdflib
from whyis import nanopub
import datetime
import pytz
import dateutil.parser
from dateutil.tz import tzlocal
from werkzeug.datastructures import FileStorage
from werkzeug.http import http_date
from setlr import FileLikeFromIter
import re
import os
from requests_testadapter import Resp
import mimetypes
import traceback
import sys

from whyis.namespace import np, prov, dc, sio

from .importer import Importer
from .local_file_adapter import LocalFileAdapter


class LinkedData(Importer):
    def __init__(self, prefix, url, headers=None, access_url=None,
                 format=None, modified_headers=None, postprocess_update=None,
                 postprocess=None, min_modified=0, import_once=False,
                 replace=[]):
        self.prefix = prefix
        self.url = url
        self.detect_url = url.split("%s")[0]
        self.headers = headers
        self.modified_headers = modified_headers
        self.format = format
        self.min_modified = min_modified
        self.import_once = import_once
        self.replace = replace
        if access_url is not None:
            self.access_url = access_url
        else:
            self.access_url = "%s"
        if callable(self.access_url):
            self._get_access_url = self.access_url
        else:
            self._get_access_url = lambda entity_name: self.access_url % entity_name
        self.postprocess_update = postprocess_update
        self.postprocess = postprocess

    def resource_matches(self, entity):
        return entity.startswith(self.detect_url)

    def matches(self, entity_name):
        # print entity_name, self.prefix, entity_name.startswith(self.prefix)
        return entity_name.startswith(self.prefix)

    def map(self, entity_name):
        fragment = self.get_fragment(entity_name)
        return rdflib.URIRef(self.url % fragment)

    def get_fragment(self, entity_name):
        fragment = entity_name[len(self.prefix):]
        return fragment

    def modified(self, entity_name):
        u = self._get_access_url(entity_name)
        print("accessing at", u)
        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        requests_session.mount('file:///', LocalFileAdapter())
        r = requests_session.head(u, headers=self.modified_headers, allow_redirects=True)
        # print "Modified Headers", r.headers
        if 'Last-Modified' in r.headers:
            result = dateutil.parser.parse(r.headers['Last-Modified'])
            # print result, r.headers['Last-Modified']
            return result

        return None

    def fetch(self, entity_name):
        u = self._get_access_url(entity_name)
        r = requests.get(u, headers=self.headers, allow_redirects=True)
        g = rdflib.Dataset()
        local = g.graph(rdflib.BNode())
        text = r.text
        for pattern, repl in self.replace:
            text = re.sub(pattern, repl, text)
        local.parse(data=text, format=self.format)
        # print self.postprocess_update
        if self.postprocess_update is not None:
            commands = self.postprocess_update
            if isinstance(commands, str):
                commands = [commands]
            for command in commands:
                # print "update postprocess query."
                g.update(command)
        if self.postprocess is not None:
            p = self.postprocess
            p(g)
        # print g.serialize(format="trig")
        return rdflib.ConjunctiveGraph(identifier=local.identifier, store=g.store)
