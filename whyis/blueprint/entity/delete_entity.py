from flask import current_app
from flask_login import login_required
from whyis.decorator import conditional_login_required
from rdflib import *

from .entity_blueprint import entity_blueprint

@entity_blueprint.route('/about', methods=['DELETE'])
@entity_blueprint.route('/<path:name>', methods=['DELETE'])
@login_required
def delete_entity(name=None, format=None, view=None):
    current_app.db.store.nsBindings = {}
    entity, content_type = current_app.get_entity_uri(name, format)
    if not current_app._can_edit(entity):
        return '<h1>Not Authorized</h1>', 401
    if (entity, RDF.type, current_app.NS.np.Nanopublication) in current_app.db:
        current_app.nanopub_manager.retire(entity)
    else:
        current_app.delete_file(entity)
    return '', 204
