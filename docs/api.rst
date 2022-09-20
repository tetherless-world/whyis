Whyis HTTP API Documentation
============================

.. http:get:: /(path:name)

   Return the specified view for the specified entity,
   defined by the entity at (lodprefix)/(path:name).
   If the LOD_PREFIX is set to http://example.com and the path name is "foobar",
   the requested entity will be http://example.com/foobar.

   **Example request**:

   .. sourcecode:: http

      GET /foobar HTTP/1.1
      Host: example.com

   :query view: one of the registered views. Default value is "view".
   :query uri: the URI of the requested entity. Must be a valid URI.
   :statuscode 200: no error
   :statuscode 404: The view is not defined for this entity.

.. http:post:: /(path:name)

   Return the specified view for the specified entity,
   defined by the entity at (lodprefix)/(path:name).
   If the LOD_PREFIX is set to http://example.com and the path name is "foobar",
   the requested entity will be http://example.com/foobar.

   **Example request**:

   .. sourcecode:: http

      GET /foobar HTTP/1.1
      Host: example.com

   :query view: one of the registered views. Default value is "view".
   :query uri: the URI of the requested entity. Must be a valid URI.

   :statuscode 200: no error
   :statuscode 404: The view is not defined for this entity.

.. http:post:: /pub

   Add a nanopublication to the graph. Returns the URI of the first (or only)
   nanopublication in the posted graph. It will wrap non-graph RDF files and
   named graphs in auto-generated nanopublications.

   **Example request**:

   .. sourcecode:: http

      POST /pub HTTP/1.1
      Host: example.com
      Content-Type: text/turtle

      <http://dbpedia.org/John_Lennon> a <http://schema.org/Person>.

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 CREATED
      Location: http://example.com/pub/NTkxNzIyLjI5MzI1ODIwMjE

   :statuscode 201: no error
   :statuscode 400: RDF parse error.

.. http:get:: /sparql

  Protocol clients may send protocol requests via the HTTP GET method.
  When using the GET method, clients must URL percent encode all parameters
  and include them as query parameter strings with the names given above
  [RFC3986].

  HTTP query string parameters must be separated with the ampersand (&)
  character. Clients may include the query string parameters in any order.

  The HTTP request MUST NOT include a message body.

  **Example request**:

  .. sourcecode:: http

     GET /sparql?query=select+?person+where+{+?person+a+<http://schema.org/Person>.} HTTP/1.1
     Host: example.com
     Accept: application/json

  **Example response**:

  .. sourcecode:: http

     HTTP/1.1 200 OK
     Content-Type: application/json

     {
       "head": { "vars": [ "person" ]
       } ,
       "results": {
         "bindings": [
           {
             "person": { "type": "uri" , "value": "http://dbpedia.org/John_Lennon" }
           }
         ]
       }
     }

  :query query: SPARQL-conformant query.
  :query default-graph-uri: The RDF Dataset for a query may be specified
                      either via the default-graph-uri and named-graph-uri
                      parameters in the SPARQL Protocol or in the SPARQL query
                      string using the FROM and FROM NAMED keywords.
  :query named-graph-uri: The RDF Dataset for a query may be specified either
                      via the default-graph-uri and named-graph-uri parameters
                      in the SPARQL Protocol or in the SPARQL query string using
                      the FROM and FROM NAMED keywords.
  :reqheader Accept: the response content type depends on
                     :mailheader:`Accept` header, one of the acceptable content
                     types for SPARQL.
  :statuscode 200: no error
  :statuscode 400: The SPARQL query supplied in the request is not a legal
                  sequence of characters in the language defined by the SPARQL
                  grammar.
  :statuscode 500: The service fails to execute the query. SPARQL Protocol
                  services may also return a 500 response code if they refuse
                  to execute a query. This response does not indicate whether
                  the server may or may not process a subsequent, identical
                  request or requests.
