from flask import current_app, request, redirect
from flask_login import login_required
from whyis.decorator import conditional_login_required

from .entity_blueprint import entity_blueprint

import rdflib
from urllib.parse import urlencode

@entity_blueprint.route('/<path:name>', methods=['POST'])
@entity_blueprint.route('/about', methods=['POST'])
@login_required
def post_entity(name=None, format=None, view=None):
    current_app.db.store.nsBindings = {}
    entity, content_type = current_app.get_entity_uri(name, format)
    files = [y for x, y in request.files.items(multi=True)]
    print ("uploading file",entity)
    if len(files) == 0:
        return redirect(request.url)
    upload_type = rdflib.URIRef(request.form['upload_type'])
    current_app.add_files(entity, files,
                    upload_type=upload_type)
    url = "/about?%s" % urlencode(dict(uri=str(entity), view="view"))
    print ("redirecting to",url)
    return redirect(url)
