import requests
from flask import request, redirect, url_for, current_app, Response

from whyis.blueprint.sparql import sparql_blueprint
from whyis.decorator import conditional_login_required
from setlr import FileLikeFromIter


@sparql_blueprint.route('/sparql', methods=['GET', 'POST'])
@conditional_login_required
def sparql_view():
    has_query = False
    for arg in list(request.args.keys()):
        if arg.lower() == "update":
            return "Update not allowed.", 403
        if arg.lower() == 'query':
            has_query = True
    if request.method == 'GET' and not has_query:
        return redirect(url_for('.sparql_form'))
    
    # Check if store has raw_sparql_request method (all drivers should now have this)
    if hasattr(current_app.db.store, 'raw_sparql_request'):
        # Use the store's authenticated request method
        try:
            if request.method == 'GET':
                headers = {}
                headers.update(request.headers)
                if 'Content-Length' in headers:
                    del headers['Content-Length']
                
                req = current_app.db.store.raw_sparql_request(
                    method='GET',
                    params=dict(request.args),
                    headers=headers
                )
            elif request.method == 'POST':
                if 'application/sparql-update' in request.headers.get('content-type', ''):
                    return "Update not allowed.", 403
                if 'update' in request.values:
                    return "Update not allowed.", 403
                
                req = current_app.db.store.raw_sparql_request(
                    method='POST',
                    headers=dict(request.headers),
                    data=request.get_data()
                )
        except NotImplementedError as e:
            # Local stores don't support proxying - return error
            return str(e), 501
        except Exception as e:
            # Log and return error
            current_app.logger.error(f"SPARQL request failed: {str(e)}")
            return f"SPARQL request failed: {str(e)}", 500
    else:
        # Fallback for stores without raw_sparql_request (should not happen)
        # This is the old behavior - direct HTTP request without authentication
        if request.method == 'GET':
            headers = {}
            headers.update(request.headers)
            if 'Content-Length' in headers:
                del headers['Content-Length']
            req = requests.get(current_app.db.store.query_endpoint,
                               headers=headers, params=request.args, stream=True)
        elif request.method == 'POST':
            if 'application/sparql-update' in request.headers.get('content-type', ''):
                return "Update not allowed.", 403
            if 'update' in request.values:
                return "Update not allowed.", 403
            req = requests.post(current_app.db.store.query_endpoint,
                                headers=request.headers, data=request.values, stream=True)
    
    # Return the response
    response = Response(FileLikeFromIter(req.iter_content()),
                        content_type=req.headers.get('content-type', 'application/sparql-results+xml'))
    return response, req.status_code
