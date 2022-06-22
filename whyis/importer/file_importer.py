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

from .linked_data import LinkedData
from .local_file_adapter import LocalFileAdapter


class FileImporter(LinkedData):
    def __init__(self, prefix, url, file_types=None, **kwargs):
        LinkedData.__init__(self, prefix, url, **kwargs)
        self.file_types = file_types

    def fetch(self, entity_name):
        u = self._get_access_url(entity_name)
        requests_session = requests.session()
        requests_session.mount('file://', LocalFileAdapter())
        requests_session.mount('file:///', LocalFileAdapter())
        r = requests_session.get(u, headers=self.headers, allow_redirects=True, stream=True)
        npub = nanopub.Nanopublication()
        if 'content-disposition' in r.headers:
            d = r.headers['content-disposition']
            fname = re.findall("filename=(.+)", d)
        else:
            fname = entity_name.split('/')[-1]
        content_type = r.headers.get('content-type')

        if self.file_types is not None:
            for file_type in self.file_types:
                npub.assertion.add((entity_name, rdflib.RDF.type, file_type))
        f = FileStorage(FileLikeFromIter(r.iter_content()), fname, content_type=content_type)
        print(fname, content_type)
        old_nanopubs = self.app.add_file(f, entity_name, npub)
        npub.assertion.add((entity_name, self.app.NS.RDF.type, self.app.NS.pv.File))

        # old_np variable unused
        for _, old_np_assertion in old_nanopubs:
            npub.pubinfo.add((npub.assertion.identifier, self.app.NS.prov.wasRevisionOf, old_np_assertion))

        return npub
