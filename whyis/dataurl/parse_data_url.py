import binascii

# try:
from urllib.parse import unquote_to_bytes
# except:
#    from urllib.parse import unquote
#    def unquote_to_bytes(*args, **kwargs):
#        return toBytes(unquote(*args, **kwargs))


def parse_data_url(url):
    scheme, data = url.split(":",1)
    assert scheme == "data", "unsupported scheme: "+scheme
    content_type, data = data.split(",",1)
    # base64 urls might have a padding which might (should) be quoted:
    data = unquote_to_bytes(data)
    if content_type.endswith(";base64"):
        return binascii.a2b_base64(data), content_type[:-7] or None
    return data, content_type or None
