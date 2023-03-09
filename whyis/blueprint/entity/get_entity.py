from flask import current_app, request, Response, make_response
from rdflib import ConjunctiveGraph
from werkzeug.exceptions import abort
from depot.middleware import FileServeApp

from .entity_blueprint import entity_blueprint
from whyis.data_extensions import DATA_EXTENSIONS
from whyis.data_formats import DATA_FORMATS
from whyis.decorator import conditional_login_required

import sadi.mimeparse

from whyis.html_mime_types import HTML_MIME_TYPES

@entity_blueprint.route('/about.<format>', methods=['GET'])
@entity_blueprint.route('/<path:name>', methods=['GET'])
@entity_blueprint.route('/<path:name>.<format>', methods=['GET'])
@entity_blueprint.route('/', methods=['GET'])
@entity_blueprint.route('/home', methods=['GET'])
@entity_blueprint.route('/about', methods=['GET'])
@conditional_login_required
def view(name=None, format=None, view=None):
    current_app.db.store.nsBindings = {}
    entity, content_type = current_app.get_entity_uri(name, format)

    resource = current_app.get_resource(entity)

    # 'view' is the default view
    # print("using resource with these statements", len(resource.graph))
    fileid = resource.value(current_app.NS.whyis.hasFileID)
    print(resource.identifier, current_app.NS.whyis.hasFileID, fileid)
    if fileid is not None and 'view' not in request.args:
        print("Using File ID",fileid)
        fileid = fileid.value
        f = None
        if current_app.nanopub_depot is not None and current_app.nanopub_depot.exists(fileid):
            f = current_app.nanopub_depot.get(fileid)
        elif current_app.file_depot.exists(fileid):
            f = current_app.file_depot.get(fileid)
            print("Found File",f)
        if f is not None:
            fsa = FileServeApp(f, current_app.config["FILE_ARCHIVE"].get("cache_max_age",3600*24*7))
            print("Serving FSA",fsa)
            return fsa

    if content_type is None:
        content_type = request.headers['Accept'] if 'Accept' in request.headers else 'text/turtle'
    #print entity

    fmt = sadi.mimeparse.best_match([mt for mt in list(DATA_FORMATS.keys()) if mt is not None],content_type)
    if 'view' in request.args or fmt in HTML_MIME_TYPES:
        return current_app.render_view(resource)
    elif fmt in DATA_FORMATS:
        output_graph = ConjunctiveGraph()
        result, status, headers = current_app.render_view(resource, view='describe')
        output_graph.parse(data=result, format="json-ld")
        return output_graph.serialize(format=DATA_FORMATS[fmt]), 200, {'Content-Type':content_type}
    #elif 'view' in request.args or sadi.mimeparse.best_match(htmls, content_type) in htmls:
    else:
        return current_app.render_view(resource)
