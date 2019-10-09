from flask import current_app, request, Response, make_response
from rdflib import ConjunctiveGraph
from werkzeug.exceptions import abort

from .nanopub_blueprint import nanopub_blueprint
from whyis.blueprint.nanopub.nanopub_utils import get_nanopub_uri
from whyis.data_extensions import DATA_EXTENSIONS
from whyis.data_formats import DATA_FORMATS
from whyis.decorator import conditional_login_required

import sadi.mimeparse

from whyis.html_mime_types import HTML_MIME_TYPES


def render_nanopub(data, code, headers=None):
    if data is None:
        return make_response("<h1>Not Found</h1>", 404)

    entity = current_app.Entity(ConjunctiveGraph(data.store), data.identifier)
    entity.nanopub = data
    data, code, headers = current_app.render_view(entity)
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


#@nanopub_blueprint.route('/pub/<ident>',methods=['GET'])
#@nanopub_blueprint.route('/pub/<ident>.<format>', methods=['GET'])
#@conditional_login_required
def get_nanopub(ident, format=None):
    #print(request.method, 'get_nanopub()', ident)
    ident = ident.split("_")[0]
    uri = get_nanopub_uri(ident)
    result = current_app.nanopub_manager.get(uri)
    if result is None:
        #print("cannot find", uri)
        abort(404)

    content_type = None

    if format is not None and format in DATA_EXTENSIONS:
        content_type = DATA_EXTENSIONS[format]
    if content_type is None:
        content_type = request.headers['Accept'] if 'Accept' in request.headers else 'application/ld+json'
    fmt = sadi.mimeparse.best_match([mt for mt in list(DATA_FORMATS.keys()) if mt is not None],content_type)
    if 'view' in request.args or fmt in HTML_MIME_TYPES:
        return render_nanopub(result, 200)
    elif fmt in DATA_FORMATS:
        response = Response(result.serialize(format=DATA_FORMATS[fmt]))
        response.headers = {'Content-type': fmt}
        return response, 200
