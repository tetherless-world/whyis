import requests
from flask import request, redirect, url_for, current_app, Response

from whyis.blueprint.sparql import sparql_blueprint
from whyis.decorator import conditional_login_required
from setlr import FileLikeFromIter


# HTTP headers that should not be forwarded when proxying requests
# These are hop-by-hop headers or headers that will be set by the requests library
HOP_BY_HOP_HEADERS = [
    'Host', 'Content-Length', 'Connection', 'Keep-Alive',
    'Proxy-Authenticate', 'Proxy-Authorization', 'TE', 'Trailers',
    'Transfer-Encoding', 'Upgrade'
]


def filter_headers_for_proxying(headers):
    """
    Filter out hop-by-hop headers that should not be forwarded when proxying.
    
    Performs case-insensitive header matching to comply with HTTP standards,
    which specify that header names are case-insensitive.
    
    Args:
        headers: Flask headers object or dict of headers
        
    Returns:
        dict: Filtered headers suitable for forwarding (with hop-by-hop headers removed)
    """
    filtered = dict(headers)
    # Use case-insensitive comparison since HTTP headers are case-insensitive
    headers_lower = {k.lower(): k for k in filtered.keys()}
    for header in HOP_BY_HOP_HEADERS:
        header_lower = header.lower()
        if header_lower in headers_lower:
            del filtered[headers_lower[header_lower]]
    return filtered


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
                
                # Get the raw data BEFORE accessing request.values
                # because accessing request.values consumes the input stream
                raw_data = request.get_data()
                
                if 'update' in request.values:
                    return "Update not allowed.", 403
                
                # Filter headers for proxying
                headers = filter_headers_for_proxying(request.headers)
                
                req = current_app.db.store.raw_sparql_request(
                    method='POST',
                    headers=headers,
                    data=raw_data
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
            
            # Get raw data before accessing request.values
            raw_data = request.get_data()
            
            if 'update' in request.values:
                return "Update not allowed.", 403
            
            # Filter headers for proxying
            headers = filter_headers_for_proxying(request.headers)
            
            req = requests.post(current_app.db.store.query_endpoint,
                                headers=headers, data=raw_data, stream=True)
    
    # Return the response
    response = Response(FileLikeFromIter(req.iter_content()),
                        content_type=req.headers.get('content-type', 'application/sparql-results+xml'))
    return response, req.status_code
