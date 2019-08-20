import io

from .parse_data_url import parse_data_url

from werkzeug.datastructures import FileStorage


class DataURLStorage(FileStorage):
    def __init__(self, url, filename=None, name=None):
        data, content_type = parse_data_url(url)
        stream = io.BytesIO(data)
        FileStorage.__init__(self, stream=stream, filename=filename, content_type=content_type, content_length=len(data))
