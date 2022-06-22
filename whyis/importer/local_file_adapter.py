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
import puremagic as magic
import mimetypes
import traceback
import sys

from whyis.namespace import np, prov, dc, sio


class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        mtime = os.path.getmtime(file_path)
        dt = datetime.datetime.fromtimestamp(mtime, tzlocal())
        mimetype = mimetypes.guess_type(file_path)[0]
        if mimetype is None and magic is not None:
            t = magic.from_file(file_path, mime=True)
            if len(t) > 0:
                mimetype = t[0].mime_type
        headers = {"Last-Modified": http_date(dt)}
        if mimetype is not None:
            headers['Content-Type'] = mimetype
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff, headers=headers)
            r = self.build_response(request, resp)
            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):
        return self.build_response_from_file(request)
