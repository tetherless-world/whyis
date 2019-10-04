from flask import current_app
from flask_login import login_required

from whyis.blueprint.nanopub import nanopub_blueprint
from whyis.blueprint.nanopub.nanopub_utils import get_nanopub_uri, get_nanopub_graph, prep_nanopub
from whyis.namespace import NS


@nanopub_blueprint.route('/pub/<ident>', methods=['PUT'])
@login_required
def put_nanopub(ident):
    #print(request.method, 'put_nanopub()', ident)
    nanopub_uri = get_nanopub_uri(ident)
    inputGraph = get_nanopub_graph()
    old_nanopub = prep_nanopub(nanopub_uri, inputGraph)
    for nanopub in current_app.nanopub_manager.prepare(inputGraph):
        nanopub.pubinfo.set((nanopub.assertion.identifier, NS.prov.wasRevisionOf, old_nanopub.assertion.identifier))
        current_app.nanopub_manager.retire(nanopub_uri)
        current_app.nanopub_manager.publish(nanopub)
