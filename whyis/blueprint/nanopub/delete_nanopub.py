from flask_login import login_required

from .nanopub_blueprint import nanopub_blueprint


@nanopub_blueprint.route('/pub/<ident>', methods=['DELETE'])
@login_required
def delete_nanopub(ident):
    #print(request.method, 'delete_nanopub()', ident)
    ident = ident.split("_")[0]
    uri = _get_uri(ident)
    if not app._can_edit(uri):
        return '<h1>Not Authorized</h1>', 401
    current_app.nanopub_manager.retire(uri)
    return '', 204
