import requests
from flask import request, redirect, url_for, current_app, Response, jsonify
from .cql_blueprint import cql_blueprint
from whyis.decorator import conditional_login_required
from ..plugin import CypherToSparqlTranslator
from setlr import FileLikeFromIter


@cql_blueprint.route('/cql', methods=['GET', 'POST'])
@conditional_login_required
def cql_view():
    """Handle CQL queries by translating to SPARQL and executing or returning translation."""
    has_query = False
    translate_only = False
    
    # Check for query and translate-only parameters
    for arg in list(request.args.keys()):
        if arg.lower() == "update":
            return "Update not allowed.", 403
        if arg.lower() == 'query':
            has_query = True
        if arg.lower() == 'translate-only':
            translate_only = True
    
    # Check form data for translate-only as well
    if 'translate-only' in request.values:
        translate_only = True
    
    if request.method == 'GET' and not has_query:
        return redirect(url_for('.cql_form'))
    
    # Get CQL query from parameters or form data
    cql_query = None
    if request.method == 'GET':
        cql_query = request.args.get('query')
    elif request.method == 'POST':
        cql_query = request.values.get('query')
    
    if not cql_query:
        return "Missing query parameter.", 400
    
    try:
        # Get JSON-LD context from app config
        cypher_context = current_app.config.get('CYPHER_JSONLD_CONTEXT', {})
        
        # Initialize translator
        translator = CypherToSparqlTranslator(cypher_context)
        
        # Translate CQL to SPARQL
        sparql_query = translator.translate(cql_query)
        
        # If translate-only is requested, return the SPARQL query as plain text
        if translate_only:
            return Response(sparql_query, content_type='text/plain')
        
        # Otherwise, execute the SPARQL query
        if request.method == 'GET':
            headers = {}
            headers.update(request.headers)
            if 'Content-Length' in headers:
                del headers['Content-Length']
            
            # Create new parameters with the SPARQL query
            sparql_params = dict(request.args)
            sparql_params['query'] = sparql_query
            if 'translate-only' in sparql_params:
                del sparql_params['translate-only']
            
            req = requests.get(current_app.db.store.query_endpoint,
                             headers=headers, params=sparql_params, stream=True)
        elif request.method == 'POST':
            # Create new form data with the SPARQL query
            sparql_data = dict(request.values)
            sparql_data['query'] = sparql_query
            if 'translate-only' in sparql_data:
                del sparql_data['translate-only']
            
            req = requests.post(current_app.db.store.query_endpoint,
                              headers=request.headers, data=sparql_data, stream=True)
        
        response = Response(FileLikeFromIter(req.iter_content()),
                          content_type=req.headers['content-type'])
        return response, req.status_code
        
    except Exception as e:
        current_app.logger.error(f"Error processing CQL query: {e}")
        return f"Error processing CQL query: {str(e)}", 500