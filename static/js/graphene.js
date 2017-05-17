//require(["jquery", "bootstrap"], function(jquery, bootstrap) {
    $('[data-toggle="tooltip"]').tooltip()
//});

/**
 * Decode payload in the given data URI, return the result as a Buffer.
 * See [RFC2397](http://www.ietf.org/rfc/rfc2397.txt) for the specification
 * of data URL scheme.
 * @param {String} uri
 * @returns {Buffer}
 */
function decodeDataURI(uri) {

    //  dataurl    := "data:" [ mediatype ] [ ";base64" ] "," data
    //  mediatype  := [ type "/" subtype ] *( ";" parameter )
    //  data       := *urlchar
    //  parameter  := attribute "=" value
    
    var m = /^data:([^;,]+)?((?:;(?:[^;,]+))*?)(;base64)?,(.*)/.exec(uri);
    if (!m) {
        throw new Error('Not a valid data URI: "' + uri.slice(0, 20) + '"');
    }
    
    var media    = '';
    var b64      = m[3];
    var body     = m[4];
    var result   = null;
    var charset  = null;
    var mimetype = null;
    
    // If <mediatype> is omitted, it defaults to text/plain;charset=US-ASCII.
    // As a shorthand, "text/plain" can be omitted but the charset parameter
    // supplied.
    if (m[1]) {
        mimetype = m[1];
        media = mimetype + (m[2] || '');
    } else {
        mimetype = 'text/plain';
        if (m[2]) {
            media = mimetype + m[2];
        } else {
            charset = 'US-ASCII';
            media = 'text/plain;charset=US-ASCII';
        }
    }
    
    // The RFC doesn't say what the default encoding is if there is a mediatype
    // so we will return null.  For example, charset doesn't make sense for
    // binary types like image/png
    if (!charset && m[2]) {
        var cm = /;charset=([^;,]+)/.exec(m[2]);
        if (cm) {
            charset = cm[1];
        }
    }
    
    if (b64) {
        result = {value : atob(body)};
        
    } else {
        result = {value : decodeURIComponent(body)};
    }
    
    result.mimetype  = mimetype;
    result.mediatype = media;
    result.charset   = charset;
    
    return result;
}


function encodeDataURI(input, mediatype) {
    var buf;
    if (Buffer.isBuffer(input)) {
        buf = input;
        mediatype = mediatype || 'application/octet-stream';
    } else if (typeof(input) == 'string') {
        buf = new Buffer(input, 'utf8');
        mediatype = mediatype || 'text/plain;charset=UTF-8';
    } else {
        // TODO: support streams?
        throw new Error('Invalid input, expected Buffer or string');
    }
    // opinionatedly base64
    return 'data:' + mediatype + ';base64,' + buf.toString('base64');
}


//require(["d3", "angular", "jquery", 'angular-sanitize', "bootstrap" ], function () {
$( function() {
    PALETTE = [
        "#9B242D",
        "#B6985E",
        "#59452A",
        "#8CB7C7",
        "#977C00",
        "#CE6B29",
        "#000000"
    ];

    function wordCloud(concepts) {
        var fill = d3.scale.ordinal()
            .range(PALETTE);

        var maxSize = d3.max(concepts, function(c) {return c.tfidf});
        var maxFontSize = 40;
        var minFontSize = 20;
        var w;
        var parent = d3.select(this);
        parent.each(function() {
            w = this.getBoundingClientRect().width;
        });
        var layout = d3.layout.force()
            .nodes(concepts)
            .gravity(0.5)
	    .charge(-30)
        //cloud()
            .size([w, w])
            //.words(concepts)
            //.padding(5)
            //.rotate(function() { return 0 })
            //.font("Helvetica")
            //.fontSize(function(d) { return minFontSize + (maxFontSize-minFontSize) * (d.tfidf/maxSize); })
            //.on("end", draw);

        //var root = concepts[0];
        //root.fixed = true;
        
        layout.start();
        layout.alpha(0.2);
        
        var svg = parent.append("svg")
            .attr("width", layout.size()[0])
            .attr("height", layout.size()[1])
            .attr("xmlns:xlink","http://www.w3.org/1999/xlink");
        
        var transformGroup = svg.append("g");
            //.attr("display","hide");
            //.attr("transform", "translate(" + layout.size()[0] + "," + layout.size()[1] + ")");
        var zoomGroup = transformGroup.append("g");

        var node = zoomGroup
            .selectAll("a")
            .data(concepts)
            .enter()
            .append("a")
            .attr("xlink:href", function(d) { return d.concept; })
            .attr("xlink:title", function(d) { return d.definition; })
            .style("text-decoration", "none")
            //.attr("transform", function(d,i) {
            //    console.log(d, i, i % 2, 90*(i%2));
                //d.rotated = true;
                //return "rotate("+(90*(i%2))+")";
            //})
            .append("text")
            .style("font-size", function(d) {
                //return d.size + "px";
                return minFontSize + (maxFontSize-minFontSize) * d.tfidf/maxSize; 
            })
            .style("font-family", "Helvetica")
            .style("fill", function(d, i) { return fill(i); })
            .attr("transform",function(d, i) { return "rotate("+(90*i%2)+")"})
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .text(function(d) { return d.label; });

        layout.on('tick', draw);
        var padding=4;

        padding = 4;
        function overlap (a, b) {
            return (Math.abs(a.x - b.x) * 2 <= (a.width + b.width + padding)) &&
                (Math.abs(a.y - b.y) * 2 <= (a.height + b.height + padding))
        };
        function collide(a) {
            return function(quad, x1, y1, x2, y2) {
                var dx, dy;
                if (quad.point && (quad.point !== a)) {
                    var b = quad.point;
                    if (overlap(a, b)) {
                        dy = (a.y - b.y)/d3.min([a.height, b.height]);
                        //a.y += dy;
                        //b.y -= dy;

                        if (a.y > b.y) {
                            a.y += 1;
                            b.y -= 1;
                        } else {
                            a.y -= 1;
                            b.y += 1;
                        }

                        if (a.width < averageWidth && b.width < averageWidth) {
                            dx = (a.x - b.x)/d3.min([a.width, b.width]);
                            //a.x += dx;
                            //b.x -= dx;
                            if (a.x > b.x) {
                                a.x += 1;
                                b.x -= 1;
                            } else {
                                a.x -= 1;
                                b.x += 1;
                            }
                        }
                        //lower.y += a.height/2* ((by - ay)/Math.abs(ay - by)) + dy ;

                        //dy = Math.min(ny2 - (quad.point.y - quad.point.height/2),
                        //              (quad.point.y + quad.point.height/2) - ny1) / 2;
                        //node.y -= dx;
                        //quad.point.y += dx;
                    }
                }
                return false;//overlap( a, {x: (x1+x2)/2, width:Math.abs(x2-x1), y: (y1 + y2)/2, height: Math.abs(y2-y1) });  
            };
        };

        var averageWidth = 0;
        function draw() {
            node.each(function(d) {
                var bbox = this.getBBox();
                d.width = bbox.width;
                d.height = bbox.height;
                if (d.rotated) {
                    d.height = bbox.width;
                    d.width = bbox.height;
                }
                if (d.width < d.height) {
                    console.log(d);
                }
            });
            averageWidth = d3.mean(concepts, function(d) {return d.width});
            var q = d3.geom.quadtree(concepts),
                i = 0,
                n = concepts.length;


            while (++i < n) {
                q.visit(collide(concepts[i]));
            }
            node.attr("transform", function(d, i) {
                return "translate(" + [d.x, d.y] + ") ";
            })
            
            zoomGroup.each(function() {
                var bbox = this.getBBox();
                var zoomFactor = d3.min([layout.size()[0]/bbox.width, layout.size()[1]/bbox.height]);
                zoomGroup.attr("transform", "translate("+(0-bbox.x*zoomFactor)+", "+(0-bbox.y*zoomFactor)+") "+
                               "scale("+zoomFactor+", "+zoomFactor+") ");
            });
            transformGroup.each(function() {
                var bbox = this.getBBox();
                svg.attr("height", bbox.height);
            });
        }
    };

    function radianToDegree(r) {
        return r * 180 / Math.PI;
    };
    
    function relatedWheel(related) {
        var fill = d3.scale.ordinal()
            .range(PALETTE);
        var n = related.slice();

        var size = 500;
        var parent = d3.select(this);
        parent.each(function() {
            size = this.getBoundingClientRect().width;
        });


        var svg = parent.append("svg")
            .attr("width", size)
            .attr("height", size)
            .attr("xmlns:xlink","http://www.w3.org/1999/xlink");
        
        var transformGroup = svg.append("g")
            .attr("transform", "translate(" + size/2 + "," + size/2 + ")");

        var radius = size/5;

        var partition = d3.layout.partition()
            .size([2 * Math.PI, radius * radius])
            .value(function(d) {
                return d.factor * (d.nodes.length) + 1;
            });

        var root = {
            children: related
        };
        var nodes = partition.nodes(root).slice(1);
        nodes = n;
        var offset = nodes[0].dx / 2;

        var spanAngle = offset * nodes[0].factor;

        

        var rotateGroup = transformGroup.append("g")
            .attr("transform", "rotate("+(90- radianToDegree(offset))+")");

        var accumX = 0;

        nodes.forEach(function( d) {
            d.x = accumX;
            accumX += d.dx;
        });
        
        var arc = d3.svg.arc()
            .startAngle(function(d) { return  0; })
            .endAngle(function(d) { return d.dx - 0.1; })
            .innerRadius(function(d) { return radius; })
            .outerRadius(function(d) { return radius + radius * (1-d.distance) * d.factor; });


        var nodeTypeGroup = rotateGroup.selectAll("g.NodeType")
            .data(nodes)
            .enter()
            .append("g")
            .classed("NodeType",true)
            .attr("transform",function(d) {
                return "rotate("+ radianToDegree(d.x + 0.05)  + ")";
            });

        var path = nodeTypeGroup.append("svg:path")
            .attr("display", function(d) { return d.depth ? null : "none"; })
            .attr("d", arc)
            .style("fill", function(d) {
                return d.color;
            })
            .style("opacity", 0.25);

        nodes.forEach(function(d) {
            d.layout = d3.scale.ordinal()
                .domain(d.nodes.map(function (n) {
                    n.nodeType = d;
                    return n.node;
                }))
                .rangePoints([0, d.dx - 0.1], (d.dx)/d.nodes.length + 1);
        });

        var barScale = d3.scale.linear().domain([1,0]).range([0, radius/4]);
        
        var relatedNodeGroup = nodeTypeGroup.selectAll("g.Node")
            .data(function(d) {return d.nodes})
            .enter()
            .append("g")
            .classed("Node", true)
            .attr("transform", function(d) {
                return "rotate("+radianToDegree(d.nodeType.layout(d.node)) + ") translate(0,"+radius+")";
            })
            .append('a').attr('href',function(d) { return d.node+"?wheel"; });
        relatedNodeGroup
            .append("rect")
            .attr("x", -10)
            .attr("width",20)
            .attr("y",function(d) {
                return - barScale(parseFloat(d.distance)) - 2 * radius;
            })
            .attr("height",function(d) { return barScale(parseFloat(d.distance))} )
            .attr("fill", function(d) { return d.nodeType.color });
        relatedNodeGroup
            .append("text")
            .attr("x", function(d) {
                var x = barScale(parseFloat(d.distance)) + 2 * radius + 4 ;
                var angle = radianToDegree(d.nodeType.x + d.nodeType.dx);
                if ( angle > 90 && angle < 270 )
                    return -x;
                else return x;
            })
            .attr("transform",function(d) {
                var angle = radianToDegree(d.nodeType.x + d.nodeType.dx);
                if ( angle > 90 && angle < 270 )
                    return "rotate(90)";
                else return "rotate(-90)";
            })
            .attr("text-anchor",function(d) {
                var angle = radianToDegree(d.nodeType.x + d.nodeType.dx);
                if ( angle > 90 && angle < 270 )
                    return "end";
                else return "start";
            })
            .attr("dominant-baseline", "middle")
            .attr("fill",function(d) { return d.nodeType.color })
            .attr("font-size", function(d) { return 14 * d.nodeType.factor})
            .text(function(d) {
                if (d.title.length > 35)
                    return  d.title.substring(0,30)+"...";
                else return d.title;
            });
    }
    
    if (typeof concepts !== 'undefined')
        d3.select("#conceptcloud").datum(concepts).each(wordCloud);

    if (typeof related !== 'undefined')
        d3.select("#relatedwheel").datum(related).each(relatedWheel);
        
    
    app = angular.module('App', ['ngSanitize', 'ngMaterial', 'lfNgMdFileInput']);
    app.config(function($interpolateProvider, $httpProvider, $locationProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
        
        var csrftoken = $('meta[name=csrf-token]').attr('content');
        $httpProvider.defaults.headers.put.X_CSRFTOKEN = csrftoken;
        $httpProvider.defaults.headers.post.X_CSRFTOKEN = csrftoken;
        $httpProvider.defaults.headers.patch.X_CSRFTOKEN = csrftoken;
        $httpProvider.defaults.headers.delete = {X_CSRFTOKEN: csrftoken};
        app.LOD_PREFIX = LOD_PREFIX;

    });

    app.factory('Service', ['$http', 'Graph', function($http, Graph) {
        function Service(endpoint) {
            
        }
        return Service;
    }]);

    app.factory('listify', function() {
        return function(x) {
            if (x.forEach) return x;
            else return [x];
        };
    });

    app.factory('Resource', ['listify', function(listify) {
        function resource (id, values) {
            var result = { 
                "@id" : id 
            };
            result.resource = function(id, values) {
                var valuesGraph = null;
                if (values && values['@graph'])
                    valuesGraph = values['@graph'];
                var result = resource(id, values);

                if (!this.resource.resources[id]) {
                    this.resource.resources[id] = result;
                    if (!this['@graph']) this['@graph'] = [];
                    this['@graph'].push(this.resource.resources[id]);
                } else {
                    result = this.resource.resources[id];
                    if (valuesGraph) {
                        valuesGraph.forEach(function(r) {
                            result.resource(r['@id'], r);
                        });
                    }
                }
                result = this.resource.resources[id];
                return result;
            };

            result.values = function(p) {
                if (!this[p]) this[p] = [];
                if (!this[p].forEach) this[p] = [this[p]];
                return this[p];
            };
            result.has = function(p, o) {
                var hasP = result[p] && (!result.forEach || result[p].length > 0);
                if ( o == null || hasP == false) {
                    return hasP;
                } else {
                    return result.values(p).filter(function(value) {
                        if (o['@id']) {
                            return value['@id'] == o['@id'];
                        }
                        if (o['@value']) o = o['@value'];
                        if (value['@value']) value = value['@value'];
                        return o == value;
                    });
                }
            }
            result.value = function(p) {
                if (result.has(p)) {
                    return result.values(p)[0];
                }
            }
            result.add = function(p, o) {
                result.values(p).push(o);
            }
            result.set = function(p, o) {
                result.po[p] = [o];
            }
            result.del = function(p) {
                delete this.po[p];
            }
            result.resource.resources = {};
            if (values) {
                if (values['@graph']) {
                    values['@graph'].forEach(function(r) {
                        result.resource(r['@id'], r);
                    });
                    delete values['@graph'];
                }
                Object.assign(result, values);
            }
            return result;
        }
        return resource;
    }]);

    app.factory('formats', [function() {
        var formats =  [
            { mimetype: "application/rdf+xml", name: "RDF/XML", extensions: ["rdf"]},
            { mimetype: "application/ld+json", name: 'JSON-LD', extensions: ["json",'jsonld']},
            { mimetype: "text/turtle", name : "Turtle", extensions: ['ttl']},
            { mimetype: "application/trig", name : "TRiG", extensions: ['trig']},
            { mimetype: "application/n-quads", name : "n-Quads", extensions: ['nq','nquads']},
            { mimetype: "application/n-triples", name : "N-Triples", extensions: ['nt','ntriples']},
        ];
        formats.lookup = {};
        formats.forEach(function(f) {
            f.extensions.forEach(function(extension) {
                formats.lookup[extension] = f;
            });
        });
        [
            { mimetype: "text/html", name : "HTML+RDFa", extensions: ['html','htm']},
            { mimetype: "text/markdown", name : "Semantic Markdown", extensions: ['html','htm']},
        ].forEach(function(f) {
            f.extensions.forEach(function(extension) {
                formats.lookup[extension] = f;
            });
        });
        return formats;
    }]);
    
    app.factory('Graph', ['$http', 'listify', function($http, listify) {
        function Resource(uri, graph) {
            var that = this;
            this.uri = uri;
            this.graph = graph;
            this.po = {};
            this.values = function(p) {
                if (!this.po[p]) this.po[p] = [];
                return this.po[p];
            };
            this.has = function(p) {
                return this.po[p] && this.po[p].length > 0;
            }
            this.value = function(p) {
                if (this.has(p)) {
                    return this.values(p)[0];
                }
            }
            this.add = function(p, o) {
                this.values(p).push(o);
            }
            this.set = function(p, o) {
                this.po[p] = [o];
            }
            this.del = function(p) {
                delete this.po[p];
            }
            this.get = function() {
                return $http.get(this.uri, {headers:{'Accept':"application/ld+json;q=1"}});
            }
            this.toJSON = function() {
                var result = {'@id':this.uri};
                Object.keys(this.po).forEach(function(key) {
                    var values = listify(that.values(key)).map(function(value) {
                        if (value.uri) return {'@id':value.uri};
                        else if (value.toIOString) {
                            return {"@value":value.toIOString(), "@type": "http://www.w3.org/2001/XMLSchema#dateTime"};
                        } else return value;
                    });
                    result[key] = values;
                });
                return result;
            }
        }
        function Graph() {
            var graph = [],
                resourceMap = {},
                ofType = {};
            graph.resource = function(uri) {
                if (!resourceMap[uri]) {
                    resourceMap[uri] = new Resource(uri, graph);
                    graph.push(resourceMap[uri]);
                }
                return resourceMap[uri];
            };
            graph.ofType = function(type) {
                if (ofType[type] == null) {
                    ofType[type] = [];
                }
                return ofType[type];
            };

            var converters = {
                'http://www.w3.org/2001/XMLSchema#dateTime': function(v) {
                    return new Date(v);
                }
            }
            graph.merge = function(json) {
                if (json == null) return;
                if (json['@id']) {
                    var resource = graph.resource(json['@id']);
                    Object.keys(json).forEach(function(key) {
                        if (key == '@id' || key == '@graph') return;
                        else if (key == '@type') {
                            listify(json[key]).forEach(function(type) {
                                resource.add('@type',graph.resource(type));
                                graph.ofType(type).push(resource);
                            });
                        } else {
                            listify(json[key]).forEach(function(o) {
                                if (o['@id']) o = graph.resource(o['@id'], graph);
                                if (o['@value']) {
                                    if (o['@type'] && converters[o['@type']])
                                        o = converters[o['@type']](o['@value']);
                                    else
                                        o = o['@value'];
                                    
                                }
                                resource.add(key,o);
                            });
                        }
                    });
                }
                if (json['@graph']) {
                    json['@graph'].forEach(graph.merge);
                }
                if (json.forEach) json.forEach(graph.merge);
            }
            return graph;
        }
        return Graph;
    }]);
    
    app.factory('RecursionHelper', ['$compile', function($compile){
        return {
            /**
             * Manually compiles the element, fixing the recursion loop.
             * @param element
             * @param [link] A post-link function, or an object with function(s) registered via pre and post properties.
             * @returns An object containing the linking functions.
             */
            compile: function(element, link){
                // Normalize the link parameter
                if(angular.isFunction(link)){
                    link = { post: link };
                }
                
                // Break the recursion loop by removing the contents
                var contents = element.contents().remove();
                var compiledContents;
                return {
                    pre: (link && link.pre) ? link.pre : null,
                    /**
                     * Compiles and re-adds the contents
                     */
                    post: function(scope, element){
                        // Compile the contents
                        if(!compiledContents){
                            compiledContents = $compile(contents);
                        }
                        // Re-add the compiled contents to the element
                        compiledContents(scope, function(clone){
                            element.append(clone);
                        });
                        
                        // Call the post-linking function, if any
                        if(link && link.post){
                            link.post.apply(null, arguments);
                        }
                    }
                };
            }
        };
    }]);

    app.factory("getLabel", ["$http", '$q', function($http, $q) {
        var promises = {}
        function getLabel(uri) {
            if (getLabel.labels[uri] === undefined && promises[uri] === undefined) {
                promises[uri] = $http.get('/about?uri='+encodeURI(uri)+"&view=label")
                    .then(function(data, status, headers, config) {
                        var label = data.data;
                        getLabel.labels[uri] = data.data;
                    });
            }
            return getLabel.labels[uri];
        };
        getLabel.labels = {};
        return getLabel;
    }]);

    app.factory("Nanopub", ["$http", "Graph", "Resource", function($http, Graph, Resource) {
        function Nanopub(about, replyTo) {
            var graph = Resource('urn:nanopub');
            graph.resource.np = graph.resource('urn:nanopub', {
                '@type' : 'http://www.nanopub.org/nschema#Nanopublication',
                'http://semanticscience.org/resource/isAbout': {'@id':about}
            });
            graph.resource.assertion = graph.resource( 'urn:nanopub_assertion', {
                '@type' : 'http://www.nanopub.org/nschema#Assertion',
                'http://www.w3.org/ns/prov#value': [{"@value":null}],
                'htth://www.w3.org/ns/prov#wasQuotedFrom':[{"@id":null}],
                'http://open.vocab.org/terms/hasContentType':[{"@value":"text/markdown"}],
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasAssertion'] = graph.resource.assertion;

            graph.resource.provenance = graph.resource( 'urn:nanopub_provenance', {
                '@type' : 'http://www.nanopub.org/nschema#Provenance',
                'http://www.w3.org/ns/prov#value':[{"@value":null}],
                'htth://www.w3.org/ns/prov#wasQuotedFrom':[{"@id":null}],
                'http://open.vocab.org/terms/hasContentType':[{"@value":"text/markdown"}]
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasProvenance'] = graph.resource.provenance;
            graph.resource.provenance.resource.assertion = graph.resource.provenance.resource('urn:nanopub_assertion');

            graph.resource.pubinfo = graph.resource( 'urn:nanopub_publication_info', {
                '@type' : 'http://www.nanopub.org/nschema#PublicationInfo',
                'http://www.w3.org/ns/prov#value': [{"@value":null}],
                'htth://www.w3.org/ns/prov#wasQuotedFrom':[{"@id":null}],
                'http://open.vocab.org/terms/hasContentType':[{"@value":"text/markdown"}],
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasPublicationInfo'] = graph.resource.pubinfo;
            graph.resource.pubinfo.resource.assertion = graph.resource.pubinfo.resource('urn:nanopub_assertion');

            if (replyTo) {
                graph.resource.pubinfo.resource.assertion['http://rdfs.org/sioc/ns#reply_of'] = graph.resource.pubinfo.resource(replyTo);
            }
            return graph;
        }
        function processNanopubs(response) {
            console.log(response);
            var graphs = Resource(null, {'@graph': response.data});
            var nanopubs = [];
            var graphMap = {};
            function nanopubComparator(a,b) {
                return b.resource.pubinfo.resource.assertion['http://purl.org/dc/terms/created'] -
                    a.resource.pubinfo.resource.assertion['http://purl.org/dc/terms/created'];
            }
            if (graphs['@graph'])
                graphs['@graph'].forEach(function(graph) {
                    graphMap[graph['@id']] = graph;
                    graph.resource.self = graph.resource(graph['@id']);
                    if (graph.resource.self.has('http://www.nanopub.org/nschema#hasAssertion')) {
                        nanopubs.push(graph);
                        graph.resource.assertion = graph.resource.self.value('http://www.nanopub.org/nschema#hasAssertion');
                        graph.resource.provenance = graph.resource.self.value('http://www.nanopub.org/nschema#hasProvenance');
                        graph.resource.pubinfo = graph.resource.self.value('http://www.nanopub.org/nschema#hasPublicationInfo');
                        if (graph.resource.replies === undefined) graph.resource.replies = [];
                    }
                });
            nanopubs.forEach(function(np) {
                if (graphMap[np.resource.assertion['@id']]) {
                    np.resource.assertion = graphMap[np.resource.assertion['@id']];
                    np.resource.assertion = np.resource(np.resource.assertion['@id'],np.resource.assertion);
                }
                if (graphMap[np.resource.provenance['@id']]) {
                    np.resource.provenance = graphMap[np.resource.provenance['@id']];
                    np.resource.provenance = np.resource(np.resource.provenance['@id'],np.resource.provenance);
                    np.resource.provenance.resource.assertion = np.resource.provenance.resource(np.resource.assertion['@id']);
                }
                if (graphMap[np.resource.pubinfo['@id']]) {
                    np.resource.pubinfo = graphMap[np.resource.pubinfo['@id']];
                    np.resource.pubinfo = np.resource(np.resource.pubinfo['@id'],np.resource.pubinfo);
                    np.resource.pubinfo.resource.assertion = np.resource.pubinfo.resource(np.resource.assertion['@id']);
                    console.log(np, np.resource.pubinfo.resource.assertion);

                    if (np.resource.pubinfo.resource.assertion['http://rdfs.org/sioc/ns#reply_of']) {
                        var parent = graphMap[np.resource.pubinfo.resource.assertion['http://rdfs.org/sioc/ns#reply_of'][0]['@id']];
                        if (parent.resource.replies === undefined) parent.resource.replies = [];
                        parent.resource.replies.push(np);
                        parent.resource.replies = parent.resource.replies.sort(nanopubComparator);
                    }
                }
            })
            var topNanopubs = nanopubs.filter(function(nanopub) {
                return !nanopub.resource.pubinfo.resource || !nanopub.resource.pubinfo.resource.assertion.has('http://rdfs.org/sioc/ns#reply_of');
            });
            topNanopubs = topNanopubs.sort(nanopubComparator).map(function(nanopub) {
                nanopub.resource.newNanopub = Nanopub(nanopub.resource.self.value('http://semanticscience.org/resource/isAbout')['@id'],
                                             nanopub['@id']);
                return nanopub;
            });
            console.log(topNanopubs);
            return topNanopubs;
        }
        Nanopub.list = function(about) {
            return $http.get(about, {headers:{'Accept':"application/ld+json"}, responseType:"json"})
                .then(processNanopubs);
        }
        Nanopub.update = function(nanopub) {
            return $http.put(nanopub['@id'], nanopub,{headers:{'ContentType':"application/ld+json"}, responseType:"json"});
        };
        Nanopub.save = function(nanopub) {
            return $http.post('/pub', nanopub,
                              {headers:{'ContentType':"application/ld+json"}, responseType:"json"});
        }
        Nanopub.delete = function(nanopub) {
            return $http.delete(nanopub['@id']);
        }
        return Nanopub;
    }]);
    
    app.directive("newnanopub",['Nanopub','formats', function(Nanopub, formats) {
        return {
            restrict: "E",
            require: "^nanopubs",
            scope: {
                nanopub: "=",
                verb: "@",
                save: "&onSave",
                editing: "@"
            },
            templateUrl: '/static/html/newNanopub.html',
            link: function (scope, element, attrs, nanopubsCtrl) {
                scope.currentGraph = "assertion";
                scope.formats = formats;
                scope.graphs =  ['assertion','provenance','pubinfo'];
                scope.isArray = function(variable) {
                    if (variable === undefined || variable === null) return false;
                    if (typeof variable === 'string' || variable instanceof String) return false;
                    return typeof variable === 'Array' || variable instanceof Array || variable.constructor === Array;
                };
                scope.filesUpdated = function(graph) {
                    console.log(graph);
                }
            },
        };
    }]);

    app.directive('fileModel', ['$parse', 'formats', function ($parse, formats) {
        return {
            fileModel: 'A',
            scope: {
                fileModel: "=",
                format: "="
            },
            link: function(scope, element, attrs) {
                element.bind('change', function(changeEvent){
                    var reader = new FileReader();
                    var extension = changeEvent.target.files[0].name.split(".").slice(-1)[0];
                    var format = formats.lookup[extension];
                    if (format !== undefined)
                        scope.format = format.mimetype;
                    reader.onload = function (loadEvent) {
                        scope.$apply(function () {
                            scope.fileModel = decodeDataURI(loadEvent.target.result).value;
                            
                        });
                    }
                    reader.readAsDataURL(changeEvent.target.files[0]);
                });
            }
        };
    }]);
    
    app.directive("nanopubs", ["Nanopub", "$sce", "getLabel", function(Nanopub, $sce, getLabel) {
        return {
            restrict: "E",
            scope: {
                resource: "@",
                disableNanopubing: "="
            },
            templateUrl: '/static/html/nanopubs.html',
            controller: ['$scope', function ($scope) {
                $scope.current_user = USER;
                $scope.Nanopub = Nanopub;
                $scope.getLabel = getLabel;
                $scope.canEdit = function(nanopub) {
                    //console.log( USER.uri, nanopub.resource.pubinfo);
                    return true;//USER.admin == "True"; ||
                        //nanopub.resource.pubinfo.resource.assertion.has('http://purl.org/dc/terms/contributor', {'@id':USER.uri});
                };
                //$scope.$watch('resource', function(newval) {
                //    if ($scope.about != null) {
                //        Nanopub.list($scope.resource).then($scope.update);
                //    }
                //});
                $scope.trust = $sce.trustAsHtml;
                $scope.newNanopub = Nanopub($scope.resource);
                $scope.update = function(nanopubs) {
                    $scope.nanopubs = nanopubs;
                };
                $scope.deleteNanopub = function(nanopub) {
                    $scope.toDelete = nanopub;
                    $("#deleteNanopubModal").modal("show");
                };
                $scope.editNanopub = function(nanopub) {
                    nanopub.editing = true;
                };
                $scope.saveNanopub = function(nanopub) {
                    Nanopub.update(nanopub)
                        .then(function() {
                            //location.reload();
                            return Nanopub.list($scope.resource)
                        })
                    //.then($scope.update);
                };
                $scope.createNanopub = function(nanopub) {
                    Nanopub.save(nanopub).then(function() {
                        //location.reload();
                        $scope.newNanopub = Nanopub($scope.resource);
                        return Nanopub.list($scope.resource)
                    });
                };
                $scope.delete = function(nanopub) {
                    Nanopub.delete($scope.toDelete)
                        .then(function() { return Nanopub.list($scope.resource) })
                        .then($scope.update);
                    $scope.toDelete = null;
                }
                this.update = $scope.update;
                Nanopub.list($scope.resource).then($scope.update);
            }],
        };
    }]);

    app.controller("NanopubController",['$scope', '$http', function($scope, $http) {
    }]);
    app.controller("InsightBuilder", ['$scope', '$http', function($scope, $http) {
    }]);
    angular.bootstrap(document, ['App']);

});
