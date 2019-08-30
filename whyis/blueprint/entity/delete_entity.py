from flask import current_app
from flask_login import login_required
from whyis.decorator import conditional_login_required

from .entity_blueprint import entity_blueprint

@entity_blueprint.route('/about', methods=['DELETE'])
@entity_blueprint.route('/<path:name>', methods=['DELETE'])
@login_required
def delete_entity(name=None, format=None, view=None):
    current_app.db.store.nsBindings = {}
    entity, content_type = current_app.get_entity_uri(name, format)
    
    current_app.delete_file(entity)
    return '', 204
