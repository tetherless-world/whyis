import io
import email

from .parse_data_url import parse_data_url

# DataResponse exposes the mediatype and emulates some methods/properties of
# HTTPResponse: msg, headers, length, info, geturl, getheader and getheaders
class DataResponse(io.BytesIO):
    __slots__ = 'url','mediatype','msg','headers','length'
    def __init__(self,url):
        data, mediatype = parse_data_url(url)
        io.BytesIO.__init__(self,data)
        self.url = url
        self.mediatype = mediatype
        self.length = len(data)
        self.headers = self.msg = email.message.Message()
        if mediatype is not None:
            self.msg.add_header("Content-Type",mediatype)

    def getheader(self,name,default=None):
        headers = self.headers.get_all(name) or default
        if isinstance(headers, str) or not hasattr(headers, '__iter__'):
            return headers
        return ', '.join(headers)
    
    def getheaders(self):
        return list(self.headers.items())

    def geturl(self):
        return self.url

    def info(self):
        return self.headers
