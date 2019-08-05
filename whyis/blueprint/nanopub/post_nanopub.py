from flask import current_app
from flask_login import login_required

from whyis.blueprint.nanopub import nanopub_blueprint
from whyis.blueprint.nanopub.nanopub_utils import get_nanopub_graph, prep_nanopub


@nanopub_blueprint.route('/pub/<ident>',  methods=['POST'])
@nanopub_blueprint.route('/pub',  methods=['POST'])
@login_required
def post_nanopub(ident=None):
    #print(request.method, 'post_nanopub()', ident)
    if ident is not None:
        return put_nanopub(ident)
    inputGraph = get_nanopub_graph()
    #for nanopub_uri in inputGraph.subjects(rdflib.RDF.type, app.NS.np.Nanopublication):
    #nanopub.pubinfo.add((nanopub.assertion.identifier, app.NS.dc.created, Literal(datetime.utcnow())))
    headers = {}
    for nanopub in current_app.nanopub_manager.prepare(inputGraph):
        prep_nanopub(nanopub)
        headers['Location'] = nanopub.identifier
        current_app.nanopub_manager.publish(nanopub)

    return '', 201, headers
