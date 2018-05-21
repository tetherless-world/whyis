//require(["jquery", "bootstrap"], function(jquery, bootstrap) {
    $('[data-toggle="tooltip"]').tooltip()
//});

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

var app;
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
        
    app = angular.module('App', ['ngSanitize', 'ngMaterial', 'lfNgMdFileInput', 'ui.bootstrap', 'seco.facetedSearch','jsonLdEditor']);
    console.log("Here's the app",app);
    
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

    app.filter('urlencode', function() {
        return window.encodeURIComponent;
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

    app.directive("resourceLink",['getLabel', function(getLabel) {
        return {
            restrict: "E",
            scope: {
                uri: "=",
                label: "="
            },
            template: '<a href="'+ROOT_URL+'about?uri={{uri}}"><span ng-if="label">{{label}}</span><span ng-if="label == null">{{getLabel(uri)}}</span></a>',
            link: function (scope, element, attrs) {
                scope.getLabel = getLabel;
                //scope.$watch("uri", function(){
                //    if (scope.uri != null && scope.label == null)
                //        getLabel(scope.uri).then(function(label) {
                //            scope.label = label;
                //        });
                //});
            },
        };
    }]);    
    
    app.factory("getLabel", ["$http", '$q', function($http, $q) {
        var promises = {}
        function getLabel(uri) {
            if (getLabel.labels[uri] === undefined && promises[uri] === undefined) {
                if (!promises[uri]) {
                    var localPart = uri.split("#").filter(function(d) {return d.length > 0});
                    localPart = localPart[localPart.length-1];
                    localPart = localPart.split("/").filter(function(d) {return d.length > 0});
                    localPart = localPart[localPart.length-1];
                    getLabel.labels[uri] = localPart;
                    promises[uri] = $q.defer();
                    $http.get(ROOT_URL+'about?uri='+encodeURI(uri)+"&view=label")
                        .then(function(data, status, headers, config) {
                            if (status == 200) {
                                var label = data.data;
                                getLabel.labels[uri] = data.data;
                                promises[uri].resolve(getLabel.labels[uri]);
                            }
                        });
                }
            }
            return promises[uri].promise;
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
                'http://www.w3.org/ns/prov#wasQuotedFrom':[{"@id":null}],
                'http://open.vocab.org/terms/hasContentType':[{"@value":"text/markdown"}],
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasAssertion'] = graph.resource.assertion;

            graph.resource.provenance = graph.resource( 'urn:nanopub_provenance', {
                '@type' : 'http://www.nanopub.org/nschema#Provenance',
                'http://www.w3.org/ns/prov#value':[{"@value":null}],
                'http://www.w3.org/ns/prov#wasQuotedFrom':[{"@id":null}],
                'http://open.vocab.org/terms/hasContentType':[{"@value":"text/markdown"}]
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasProvenance'] = graph.resource.provenance;
            graph.resource.provenance.resource.assertion = graph.resource.provenance.resource('urn:nanopub_assertion');

            graph.resource.pubinfo = graph.resource( 'urn:nanopub_publication_info', {
                '@type' : 'http://www.nanopub.org/nschema#PublicationInfo'
            });
            graph.resource.np['http://www.nanopub.org/nschema#hasPublicationInfo'] = graph.resource.pubinfo;
            graph.resource.pubinfo.resource.assertion = graph.resource.pubinfo.resource('urn:nanopub_assertion');

            if (replyTo) {
                graph.resource.pubinfo.resource.assertion['http://rdfs.org/sioc/ns#reply_of'] = graph.resource.pubinfo.resource(replyTo);
            }
            return graph;
        }
        function processNanopub(response) {
            console.log(response);
            var graphs = Resource(null, {'@graph': response.data});
            var nanopubs = [];
            var graphMap = {};
            function nanopubComparator(a,b) {
                if (b.resource.pubinfo == null) {
                    if (a.resource.pubinfo == null) {
                        return 0;
                    } else {
                        return -1;
                    }
                } else {
                    if (a.resource.pubinfo == null) {
                        return 1;
                    } else {
                        return b.resource.pubinfo.resource.assertion['http://purl.org/dc/terms/created'] -
                            a.resource.pubinfo.resource.assertion['http://purl.org/dc/terms/created'];
                    }
                }
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
                if (np.resource.assertion != null && graphMap[np.resource.assertion['@id']]) {
                    np.resource.assertion = graphMap[np.resource.assertion['@id']];
                    np.resource.assertion = np.resource(np.resource.assertion['@id'],np.resource.assertion);
                }
                if (np.resource.provenance != null && graphMap[np.resource.provenance['@id']]) {
                    np.resource.provenance = graphMap[np.resource.provenance['@id']];
                    np.resource.provenance = np.resource(np.resource.provenance['@id'],np.resource.provenance);
                    np.resource.provenance.resource.assertion = np.resource.provenance.resource(np.resource.assertion['@id']);
                }
                if (np.resource.pubinfo != null && graphMap[np.resource.pubinfo['@id']]) {
                    np.resource.pubinfo = graphMap[np.resource.pubinfo['@id']];
                    np.resource.pubinfo = np.resource(np.resource.pubinfo['@id'],np.resource.pubinfo);
                    np.resource.pubinfo.resource.assertion = np.resource.pubinfo.resource(np.resource.assertion['@id']);
                }
            })
            return nanopubs[0];
        }

        function processNanopubs(response) {
            var nanopubs = response.data;
            var workMap = {};
            var npMap = {};
            function nanopubComparator(a,b) {
                if (b.updated == null) {
                    if (a.updated == null) {
                        return 0;
                    } else {
                        return -1;
                    }
                } else {
                    if (a.updated == null) {
                        return 1;
                    } else {
                        return b.updated -
                            a.updated;
                    }
                }
            }
            nanopubs.forEach(function(nanopub) {
                if (nanopub.modified) nanopub.modified = new Date(nanopub.modified);
                if (nanopub.created) nanopub.created = new Date(nanopub.created);
                if (nanopub.updated) nanopub.updated = new Date(nanopub.updated);
                workMap[nanopub.work] = nanopub;
                npMap[nanopub.np] = nanopub;
                nanopub.replies = [];
                nanopub.derivations = [];
            });
            nanopubs.forEach(function(nanopub) {
                nanopub.top = true;
                if (nanopub.derived_from && npMap[nanopub.derived_from]) {
                    npMap[nanopub.derived_from].derivations.push(nanopub);
                    nanopub.top = false;
                }
                if (nanopub.reply_of && workMap[nanopub.reply_of]) {
                    workMap[nanopub.reply_of].replies.push(nanopub);
                    nanopub.top = false;
                }
            });
            var topNanopubs = nanopubs.filter(function(nanopub) {
                return nanopub.top;
            });
            topNanopubs = topNanopubs.sort(nanopubComparator).map(function(nanopub) {
                nanopub.newNanopub = Nanopub(nanopub.about, nanopub.work);
                return nanopub;
            });
            return topNanopubs;
        }
        Nanopub.get = function(nanopub) {
            var npID = nanopub.np.split("/").slice(-1)[0]
            return $http.get(ROOT_URL+'pub/'+npID, 
                                        {headers: {'ContentType':"application/ld+json"}, responseType: "json"})
                .then(function(response, error) {
                    nanopub.graph = processNanopub(response);
                    //add [{@value: null}] and [{@id: null}] back in
                    if ( nanopub.graph.resource.assertion['http://www.w3.org/ns/prov#value'] === undefined ){
                        nanopub.graph.resource.assertion['http://www.w3.org/ns/prov#value'] = [{'@value':null}];
                    }
                    if (nanopub.graph.resource.assertion['http://www.w3.org/ns/prov#wasQuotedFrom'] === undefined) {
                        nanopub.graph.resource.assertion['http://www.w3.org/ns/prov#wasQuotedFrom'] = [{'@id':null}];
                    }
                    if ( nanopub.graph.resource.provenance['http://www.w3.org/ns/prov#value'] === undefined ){
                        nanopub.graph.resource.provenance['http://www.w3.org/ns/prov#value'] = [{'@value':null}];
                    }
                    if ( nanopub.graph.resource.provenance['http://www.w3.org/ns/prov#wasQuotedFrom'] === undefined ) {
                        nanopub.graph.resource.provenance['http://www.w3.org/ns/prov#wasQuotedFrom'] = [{'@id':null}];
                    }
                });
        };
        Nanopub.list = function(about) {
            return $http.get(ROOT_URL+"about", {params: {"uri": about, view:"nanopublications"}, responseType:"json"})
                .then(processNanopubs, function (response, error) {
                    console.log(response);
                    console.log(error);
                });
        }
        Nanopub.update = function(nanopub) {
            // console.log("nanopub inside Nanopub.update: ",nanopub);
            var npID = nanopub.np.split("/").slice(-1)[0];
            return $http.put(ROOT_URL+'pub/'+npID, nanopub.graph,{headers:{'ContentType':"application/ld+json"}, responseType:"json"});
        };
        Nanopub.save = function(nanopub) {
            //remove null values from nanopub.resource.provenance and assertion
            function notNull (value) {
                return value["@value"] === null ? false : ( value["@id"] === null ? false : true );
            }
            if (nanopub.resource) {
                nanopub.resource.provenance["http://www.w3.org/ns/prov#value"] = nanopub.resource.provenance["http://www.w3.org/ns/prov#value"].filter(notNull);
                nanopub.resource.provenance["http://www.w3.org/ns/prov#wasQuotedFrom"] = nanopub.resource.provenance["http://www.w3.org/ns/prov#wasQuotedFrom"].filter(notNull);
                nanopub.resource.assertion["http://www.w3.org/ns/prov#value"] = nanopub.resource.assertion["http://www.w3.org/ns/prov#value"].filter(notNull);
                nanopub.resource.assertion["http://www.w3.org/ns/prov#wasQuotedFrom"] = nanopub.resource.assertion["http://www.w3.org/ns/prov#wasQuotedFrom"].filter(notNull);
            }

            return $http.post(ROOT_URL+'pub', nanopub,
                              {headers:{'ContentType':"application/ld+json"}, responseType:"json"});
        }
        Nanopub.delete = function(nanopub) {
            var npID = nanopub.np.split("/").slice(-1)[0];
            // console.log("Nanopub.delete: " + npID);
            return $http.delete(ROOT_URL+'pub/'+npID);
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
            templateUrl: ROOT_URL+'static/html/newNanopub.html',
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
    
    app.directive("nanopubs", ["Resource","$http", "Nanopub", "$sce", "getLabel", function(Resource, $http, Nanopub, $sce, getLabel) {
        return {
            restrict: "E",
            scope: {
                resource: "@",
                disableNanopubing: "="
            },
            templateUrl: ROOT_URL+'static/html/nanopubs.html',
            controller: ['Resource','$scope', '$http', function (Resource, $scope, $http) {
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
                    Nanopub.get(nanopub).then(function() {
                        nanopub.editing = true;
                    });
                };
                $scope.saveNanopub = function(nanopub) {
                    Nanopub.update(nanopub)
                        .then(function() {
                            //location.reload();
                            return Nanopub.list($scope.resource).then($scope.update);
                        })
                    //.then($scope.update);
                };
                $scope.createNanopub = function(nanopub) {
                    Nanopub.save(nanopub).then(function() {
                        //location.reload();
                        $scope.newNanopub = Nanopub($scope.resource);
                        return Nanopub.list($scope.resource).then($scope.update);
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


    app.directive("searchResult", ["$http", function($http) {
        return {
            restrict: "E",
            templateUrl: ROOT_URL+'static/html/searchResult.html',

            //add scope: {} into directive so that I can bind query={{ args['query'] }}
            //from inside <search-result> in the search-view.html jinja template
            //use @ instead of = because I want string, not variable
            scope:  {
                query: "@"
            },
            link: function(scope, element, attrs) {//was scope
                scope.ROOT_URL = ROOT_URL;
                console.log('attrs: ', attrs);
                console.log('scope.query is: ', scope.query);
                $http.get("searchApi", { //either "?view=searchApi" or "searchApi"
                    'params': {'query': scope.query },
                    'resultType': 'json'
                    // 'headers' : {'Accept' : 'application/json'}
                }).then(function(response) {
                    console.log('response data: ', response.data);
                    console.log('attrs is: ', attrs)
                    scope.entities = response.data;  
                });
            }
        }
    }]);

    app.directive('searchAutocomplete', ['$timeout','$q','$log','$http', "$location", "resolveEntity",
                                         function ($timeout, $q, $log, $http, $location, resolveEntity) {
	return {
	    restrict: "E",
            scope: {
                querySearch : "&?",
                selectedItemChange : "&?",
                searchTextChange : "&?",
                newNode : "&?"
            },
	    templateUrl: ROOT_URL+'static/html/searchAutocomplete.html',
            link: function(scope, element, attrs) {
	        var self = scope;

                if (!self.querySearch) self.querySearch = function() { return resolveEntity};
                if (!self.selectedItemChange) self.selectedItemChange = function() { return selectedItemChange};
                if (!self.searchTextChange) self.searchTextChange = function() { return searchTextChange};
                if (!self.newNode) self.newNode = function() { return newNode};
                
	        //self.querySearch   = querySearch;
	        //self.selectedItemChange = selectedItemChange;
	        //self.searchTextChange   = searchTextChange;

	        newNode = function(nodeid) {
	            window.location.href = ROOT_URL+nodeid.replace(' ','_');
	        }

                self.searchText = getParameterByName("query");
	        // ******************************
	        // Internal methods
	        // ******************************


	        function searchTextChange(text) {
	            $log.info('Text changed to ' + text);
	        }

	        function selectedItemChange(item) {
	            window.location.href = ROOT_URL+'about?uri='+window.encodeURIComponent(item.node);
	        }

	        /**
	         * Create filter function for a query string
	         */
	        function createFilterFor(query) {
	            var lowercaseQuery = angular.lowercase(query);
                    
	            return function filterFn(state) {
		        return lowercaseQuery in state.value;
	            };
                    
	        }
            }
        }
    }]);

    app.service('resolveEntity', ["$http", function($http) {
	/**
	 * Search for nodes.
	 */
	function resolveEntity (query) {
            return $http.get('',{params: {view:'resolve',term:query+"*"}, responseType:'json'})
                .then(function(response) {
                    return response.data.map(function(hit) {
                        hit.value = angular.lowercase(hit.label);
                        return hit;
                    });
                });
	}
        return resolveEntity;
    }]);
    
    app.directive("latest", ["$http", 'getLabel', function($http, getLabel) {
	return {
	    restrict: "E",
	    templateUrl: ROOT_URL+'static/html/latest.html',
            link: function(scope, element, attrs) {
		scope.getLabel = getLabel;
                scope.ROOT_URL = ROOT_URL;
		$http.get(ROOT_URL+"?view=latest").then(function(response) {
		    scope.entities = response.data;
		    scope.entities.forEach(function (e) {
//			e.types = e.types.split('||').map(function(t) {
//			    return { uri: t, label: getLabel(t) };
			//			});
			//e.label = getLabel(e.about);
			e.fromNow = moment.utc(e.updated).local().fromNow();
		    });
		    console.log(response);
		});
	    }
	}
    }]);

    
    app.service("topClasses", ["$http", function($http) {
        function topClasses(ontology) {
            var query = 'prefix owl: <http://www.w3.org/2002/07/owl#>\n\
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\
select distinct ?id where {\n\
  graph ?graph {\n\
    ?id a owl:Class.\n\
    ?g a owl:Ontology.\n\
  }\n\
  <'+ontology+'> owl:imports* ?g.\n\
  optional {?id rdfs:subClassOf+ ?superClass.}\n\
  FILTER(!BOUND(?superClass))\n\
  FILTER (!ISBLANK(?id))\n\
  FILTER ( !strstarts(str(?id), "bnode:") )\n\
}\n\
';
            return $http.get(ROOT_URL+'sparql', {params : {query : query, output: 'json'}, responseType: 'json'})
                .then(function(data) {
                    return data.data.results.bindings.map(function(row) {
                        return row.id.value;
                    });
                });
        }
        return topClasses;
    }]);
    /*
     * DBpedia service
     * Handles SPARQL queries and defines facet configurations.
     */
    app.service('ontologyService', function(FacetResultHandler, topClasses) {

        /* Public API */

        // Get the results from DBpedia based on the facet selections.
        this.getResults = getResults;
        // Get the facet definitions.
        this.getFacets = getFacets;
        // Get the facet options.
        this.getFacetOptions = getFacetOptions;

        /* Implementation */

        // Facet definitions
        // 'facetId' is a "friendly" identifier for the facet,
        //  and should be unique within the set of facets.
        // 'predicate' is the property that defines the facet (can also be
        //  a property path, for example).
        // 'name' is the title of the facet to show to the user.
        // If 'enabled' is not true, the facet will be disabled by default.
        var facets = {
            // Text search facet for names
            name: {
                facetId: 'label',
                predicate:'(rdfs:label|skos:prefLabel|skos:altLabel|dc:title|<http://xmlns.com/foaf/0.1/name>|<http://schema.org/name>)',
                enabled: true,
                name: 'Label'
            },
            // Text search facet for names
            definition: {
                facetId: 'definition',
                predicate:'(rdfs:comment|skos:definition|dc:description|dc:abstract)',
                enabled: true,
                name: 'Definition'
            },
        };

        topClasses(ontology).then(function(classes) {
            // Hierarchical facet
            facets.subclassof = {
                name: 'Super-Class',
                facetId: 'subclassof',
                predicate: 'rdfs:subClassOf*',
                hierarchy: 'rdfs:subClassOf*',
                enabled: true,
                classes: classes.map(function(d) {return "<"+d+">"})
            };
        });
        
        var endpointUrl = ROOT_URL+'sparql';

        // We are building a faceted search for classes.
        var rdfClass = '<http://www.w3.org/2002/07/owl#Class>';

        // The facet configuration also accept a 'constraint' option.
        // The value should be a valid SPARQL pattern.
        // One could restrict the results further, e.g., to writers in the
        // science fiction genre by using the 'constraint' option:
        //
        // var constraint = '?id <http://dbpedia.org/ontology/genre> <http://dbpedia.org/resource/Science_fiction> .';
        //
        // Note that the variable representing a result in the constraint should be "?id".
        //
        // 'rdfClass' is just a shorthand constraint for '?id a <rdfClass> .'
        // Both rdfClass and constraint are optional, but you should define at least
        // one of them, or you might get bad results when there are no facet selections.
        var facetOptions = {
            endpointUrl: endpointUrl, // required
            rdfClass: rdfClass, // optional
            constraint: 'graph ?graph {\n\
    ?id a owl:Class.\n\
    ?g a owl:Ontology.\n\
}\n\
<'+ontology+'> owl:imports* ?g.\n\
FILTER (!ISBLANK(?id))\n\
FILTER ( !strstarts(str(?id), "bnode:") )\n\
',
            preferredLang : 'en' // required
        };

        var prefixes =
            ' PREFIX owl: <http://www.w3.org/2002/07/owl#>\n' +
            ' PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n' +
            ' PREFIX dc: <http://purl.org/dc/terms/>\n' +
            ' PREFIX bds: <http://www.bigdata.com/rdf/search#>\n' +
            ' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n\n';

        // This is the result query, with <RESULT_SET> as a placeholder for
        // the result set subquery that is formed from the facet selections.
        // The variable names used in the query will be the property names of
        // the reusulting mapped objects.
        // Note that ?id is the variable used for the result resource here,
        // as in the constraint option.
        // Variable names with a '__' (double underscore) in them will results in
        // an object. I.e. here ?work__id, ?work__label, and ?work__link will be
        // combined into an object:
        // writer.work = { id: '[work id]', label: '[work label]', link: '[work link]' }
        var queryTemplate =
        ' SELECT * WHERE {\n' +
        '  <RESULT_SET> \n' +
        '  OPTIONAL { \n'+
        '   ?id rdfs:label ?label . \n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   ?id skos:definition|rdfs:comment ?definition . \n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   ?id rdfs:subClassOf ?superclass__id . \n' +
        '   OPTIONAL { \n' +
        '    ?superclass__id rdfs:label ?superclass__label . \n' +
        '   }\n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   graph ?ontology__graph { ?id a owl:Class. ?ontology__id a owl:Ontology. }. \n' +
        '   OPTIONAL { \n' +
        '    ?ontology__id rdfs:label ?ontology__label . \n' +
        '   }\n' +
        '  }\n' +
        ' }';

        var resultOptions = {
            prefixes: prefixes, // required if the queryTemplate uses prefixes
            queryTemplate: queryTemplate, // required
            resultsPerPage: 30, // optional (default is 10)
            pagesPerQuery: 1, // optional (default is 1)
            paging: true // optional (default is true), if true, enable paging of the results
        };

        // FacetResultHandler is a service that queries the endpoint with
        // the query and maps the results to objects.
        var resultHandler = new FacetResultHandler(endpointUrl, resultOptions);

        // This function receives the facet selections from the controller
        // and gets the results from DBpedia.
        // Returns a promise.
        function getResults(facetSelections) {
            // If there are variables used in the constraint option (see above),
            // you can also give getResults another parameter that is the sort
            // order of the results (as a valid SPARQL ORDER BY sequence, e.g. "?id").
            // The results are sorted by URI (?id) by default.
            return resultHandler.getResults(facetSelections).then(function(pager) {
                // We'll also query for the total number of results, and load the
                // first page of results.
                return pager.getTotalCount().then(function(count) {
                    pager.totalCount = count;
                    return pager.getPage(0);
                }).then(function() {
                    return pager;
                });
            });
        }

        // Getter for the facet definitions.
        function getFacets() {
            return facets;
        }

        // Getter for the facet options.
        function getFacetOptions() {
            return facetOptions;
        }
    });

    /*
     * The controller.
     */
    app.controller('OntologyFacetController', function($scope, FacetHandler, ontologyService, facetUrlStateHandlerService) {
        var vm = this;

        var updateId = 0;

        // page is the current page of results.
        vm.page = [];
        vm.pageNo = 0;
        vm.getPage = getPage;
        vm.makeArray = makeArray;

        vm.disableFacets = disableFacets;

        // Listen for the facet events
        // This event is triggered when a facet's selection has changed.
        $scope.$on('sf-facet-constraints', updateResults);
        // This is the initial configuration event
        var initListener = $scope.$on('sf-initial-constraints', function(event, cons) {
            updateResults(event, cons);
            // Only listen once, then unregister
            initListener();
        });

        // Get the facet configurations from dbpediaService.
        vm.facets = ontologyService.getFacets();
        // Initialize the facet handler
        vm.handler = new FacetHandler(getFacetOptions());

        // Disable the facets while results are being retrieved.
        function disableFacets() {
            return vm.isLoadingResults;
        }

        // Setup the FacetHandler options.
        function getFacetOptions() {
            var options = ontologyService.getFacetOptions();
            options.scope = $scope;

            // Get initial facet values from URL parameters (refresh/bookmark) using facetUrlStateHandlerService.
            options.initialState = facetUrlStateHandlerService.getFacetValuesFromUrlParams();
            return options;
        }


        // Get results based on facet selections (each time the selections change).
        function updateResults(event, facetSelections) {
            // As the facets are not locked while the results are loading,
            // this function may be called again before the results have been
            // retrieved. This creates a race condition where the later call
            // may return before the first one, which leads to an inconsistent
            // state once the first returns. To avoid this we'll have a counter
            // that is incremented each time update is called, and we'll abort
            // the update if the counter has been incremented before it finishes.
            var uid = ++updateId;
            // As the user can also change the page via pagination, and introduce
            // a race condition that way, we'll want to discard any pending
            // page changes if a facet value changes. So set a boolean flag for
            // this purpose.
            vm.lock = true;
            // This variable is used to disable page selection, and display the
            // spinner animation.
            vm.isLoadingResults = true;

            // Update the URL parameters based on facet selections
            facetUrlStateHandlerService.updateUrlParams(facetSelections);

            // The dbpediaService returns a (promise of a) pager object.
            return ontologyService.getResults(facetSelections)
            .then(function(pager) {
                if (uid === updateId) {
                    vm.pager = pager;
                    vm.totalCount = pager.totalCount;
                    vm.pageNo = 1;
                    getPage(uid).then(function() {
                        vm.lock = false;
                        return vm.page;
                    });
                }
            });
        }

        // Get a page of mapped objects.
        // Angular-UI pagination handles the page number changes.
        function getPage(uid) {
            vm.isLoadingResults = true;
            // Get the page.
            // (The pager uses 0-indexed pages, whereas Angular-UI pagination uses 1-indexed pages).
            return vm.pager.getPage(vm.pageNo-1).then(function(page) {
                // Check if it's ok to change the page
                if (!vm.lock || (uid === updateId)) {
                    vm.page = page;
                    vm.isLoadingResults = false;
                }
            }).catch(function(error) {
                vm.error = error;
                vm.isLoadingResults = false;
            });
        }

        function makeArray(val) {
            return angular.isArray(val) ? val : [val];
        }
    });

    app.factory('edgeNames', function() {
        // Maps each type of edge interaction with its name.
        return {
            "http://purl.obolibrary.org/obo/CHEBI_48705": "Agonist",                   
            "http://purl.obolibrary.org/obo/MI_0190": "Molecule Connection",  
            "http://purl.obolibrary.org/obo/CHEBI_23357": "Cofactor",                  
            "http://purl.obolibrary.org/obo/CHEBI_25212": "Metabolite",                
            "http://purl.obolibrary.org/obo/CHEBI_35224": "Effector",                   
            "http://purl.obolibrary.org/obo/CHEBI_48706": "Antagonist",                
            "http://purl.obolibrary.org/obo/GO_0048018": "Receptor Agonist Activity",                     
            "http://purl.obolibrary.org/obo/GO_0030547":"Receptor Inhibitor Activity",    
            "http://purl.obolibrary.org/obo/MI_0915": "Physical Association",          
            "http://purl.obolibrary.org/obo/MI_0407": "Direct Interaction",          
            "http://purl.obolibrary.org/obo/MI_0191": "Aggregation",                   
            "http://purl.obolibrary.org/obo/MI_0914": "Association",                    
            "http://purl.obolibrary.org/obo/MI_0217": "Phosphorylation Reaction",     
            "http://purl.obolibrary.org/obo/MI_0403": "Colocalization",               
            "http://purl.obolibrary.org/obo/MI_0570": "Protein Cleavage",              
            "http://purl.obolibrary.org/obo/MI_0194": "Cleavage Reaction"             
        }
    });        
    
    app.factory("edgeTypes", function() {
        // Maps edge interaction types to values for Cytoscape visualization
        return {
            "tri" : {
                "shape": "triangle",
                "color": "#FED700",
                "uris": [
                    "http://purl.obolibrary.org/obo/CHEBI_48705", 
                    "http://purl.obolibrary.org/obo/CHEBI_23357",
                    "http://purl.obolibrary.org/obo/CHEBI_25212",
                    "http://purl.obolibrary.org/obo/MI_2254",
                    "http://purl.obolibrary.org/obo/GO_0048018"
                ],
                "filter": false
            },
            "tee" : {
                "shape": "tee",
                "color": "#BF1578",
                "uris": [
                    "http://purl.obolibrary.org/obo/CHEBI_48706",
                    "http://purl.obolibrary.org/obo/MI_2255",
                ],
                "filter": false
            },
            "cir" : {
                "shape": "circle",
                "color": "#6FCCDD",
                "uris": [
                    "http://purl.obolibrary.org/obo/GO_0005488",
                    "http://purl.obolibrary.org/obo/GO_0048037",
                    "http://purl.obolibrary.org/obo/GO_0051087",
                    "http://purl.obolibrary.org/obo/NCIT_C40468",
                    "http://purl.obolibrary.org/obo/NCIT_C40483",
                    "http://purl.obolibrary.org/obo/NCIT_C40492"
                ],
                "filter": false
            },
            "dia" : {
                "shape": "diamond",
                "color": "#7851A1",
                "uris": [
                    "http://purl.obolibrary.org/obo/PATO_0002133",
                    "http://semanticscience.org/resource/Metabolism"
                ],
                "filter": false
            },
            "squ" : {
                "shape": "square",
                "color": "#A0A0A0",
                "uris": [
                    "http://purl.obolibrary.org/obo/MI_1157",
                    "http://purl.obolibrary.org/obo/MI_0194",
                    "http://purl.obolibrary.org/obo/MI_2048",
                ],
                "filter": false
            },
            "non" : {
                "shape": "triangle",
                "color": "#A7CE38",
                "uris": [
                    "http://purl.obolibrary.org/obo/MI_0190",
                    "http://purl.obolibrary.org/obo/CHEBI_35224",
                    "http://purl.obolibrary.org/obo/MI_0407",
                    "http://purl.obolibrary.org/obo/MI_0914"
                ],
                "filter": false
            },
            "other": {
                "shape": "triangle",
                "color": "#888",
                "uris": [],
                "filter": false,
                'label' : true
            }
        }
    });
        
    app.factory("nodeTypes",function() {
        // Maps node types to values for Cytoscape visualization
        return {
            // "triangle" : {
            //     "shape": "triangle",
            //     "size": "70",
            //     "color": "#FED700",
            //     "uris": ["http://semanticscience.org/resource/activator"]
            // },
            // "star" : {
            //     "shape": "star",
            //     "size": "70",
            //     "color": "#BF1578",
            //     "uris": ["http://semanticscience.org/resource/inhibitor"]
            // },
            "square" : {
                "shape": "square",
                "size": "50",
                "color": "#EA6D00",
                "uris": ["http://purl.uniprot.org/core/Protein"]
            },
            "rect" : {
                "shape": "roundrectangle",
                "size": "60",
                "color": "#112B49",
                "uris": ["http://semanticscience.org/resource/SIO_010056"]
            },
            "circle" : {
                "shape": "ellipse",
                "size": "60",
                "color": "#16A085",
                "uris": ["http://semanticscience.org/resource/Drug"]
            },
            "other" : {
                "shape": "ellipse",
                "size": "50",
                "color": "#FF7F50",
                "uris": [],
            }
        }
    });

    app.factory("getNodeFeature",['nodeTypes', function(nodeTypes) {
        // Gets the node feature of a given uri.
        return function(feature, uris) {
            var keys = Object.keys(nodeTypes);
            for (var i = 0; i < keys.length; i++) {
                for (var j = 0; j < uris.length; j++) {
                    if (nodeTypes[keys[i]]["uris"].indexOf(uris[j]) > -1) {
                        return nodeTypes[keys[i]][feature];
                    }
                }
            }
            return nodeTypes["other"][feature];
        };
    }]);
                
                
    app.factory("getEdgeFeature", ['edgeTypes', 'edgeNames', function(edgeTypes) {
        // Gets the edge feature of a given uri.
        return function(feature, uris) {
            for (var k = 0; k < uris.length; k++) {
                var uri = uris[k];
                if (feature == "name") { return edgeNames[uri]; }
                else {
                    var keys = Object.keys(edgeTypes);
                    for (var i = 0; i < keys.length; i++) {
                        console.log(uri,keys[i], edgeTypes[keys[i]]["uris"]);
                        if (edgeTypes[keys[i]]["uris"].indexOf(uri) > -1) {
                            return edgeTypes[keys[i]][feature];
                        }
                    }
                }
            }
            return edgeTypes["other"][feature];
        }
    }]);

    app.factory("links",
                ["$http", "$q", 'getLabel', 'getEdgeFeature', 'getNodeFeature',
                 function($http, $q, getLabel, getEdgeFeature, getNodeFeature) {

          function links(entity, view, elements, update, maxP, distance) {
              if (distance == null) distance = 1;
              if (maxP == null) maxP = 0.93;
              var results = [];
              if (!elements.nodes) {
                elements.nodes = [];
                elements.nodeMap = {};
                function node(uri, label, types) {
                    if (!elements.nodeMap[uri]) {
                        elements.nodeMap[uri] = { group: 'nodes', data: { uri:uri, id: uri, label: label} };
                        var nodeEntry = elements.nodeMap[uri];
                        function processTypes() {
                            if (nodeEntry.data['@type']) {
                                var types = nodeEntry.data['@type'];
                                nodeEntry.classes = types.join(' ');
                                nodeEntry.data.shape = getNodeFeature("shape", types);
                                nodeEntry.data.color = getNodeFeature("color", types);
                            }
                        }
                        //nodeEntry.data.linecolor = "#E1EA38";
                        if (types) {
                            nodeEntry.data['@type'] = types;
                            processTypes();
                        } else {
                            nodeEntry.data.described = true;
                            $http.get(ROOT_URL+'about',{ params: {uri:uri,view:'describe'}, responseType:'json'})
                                .then(function(response) {
                                    response.data.forEach(function(x) {
                                        console.log(x);
                                        if (x['@id'] == uri) {
                                            $.extend(nodeEntry.data, x);
                                            processTypes();
                                            console.log(nodeEntry);
                                        }
                                    });
                                    if (update) update()
                                });
                        }
                        if (! nodeEntry.data.label) {
                            $http.get(ROOT_URL+'about',{ params: {uri:uri,view:'label'}})
                                .then(function(response) {
                                    nodeEntry.data.label = response.data;
                                    if (update) update();
                                });
                        }
                    }
                    return elements.nodeMap[uri];
                }
                elements.node = node;
            }
            if (!elements.edges) {
                elements.edges = [];
                elements.edgeMap = {};
                function edge(edge) {
                    var edgeKey = [edge.source, edge.link, edge.target].join(' ');
                    edge.uri = edge.link;
                    if (!elements.edgeMap[edgeKey]) {
                        elements.edgeMap[edgeKey] = { group: 'edges', data: edge };
                        var edgeEntry = elements.edgeMap[edgeKey];
                        edgeEntry.id = edgeKey;
                        if (edgeEntry.data['link_types']) {
                            var types = edgeEntry.data['link_types'];
                            edgeEntry['@types'] = types;
                            edgeEntry.classes = types.join(' ');
                            edgeEntry.data.shape = getEdgeFeature("shape", types); 
                            edgeEntry.data.color = getEdgeFeature("color", types);
                            if (getEdgeFeature("label",types) && types.length > 0) {
                                edgeEntry.data.label = types[0].label;
                            }
                        }
                        if (edgeEntry.data.zscore)
                            edgeEntry.data.width = Math.abs(edgeEntry.data.zscore) + 1;
                        else
                            edgeEntry.data.width = 1 + edgeEntry.data.probability;
                        if (edgeEntry.data.zscore < 0)
                            edgeEntry.data.negation = true;
                        //elements.edges.push(edgeEntry);
                    }
                    return elements.edgeMap[edgeKey];
                }
                elements.edge = edge;
            }

            var p = $http.get(ROOT_URL+'about',{ params: {uri:entity,view:view, }, responseType:'json'})
                .then(function(response) {
                    response.data.forEach(function(edge) {
                        if (edge.probability < maxP) {
                            console.log(edge.probability, maxP, "skipping", edge);
                            return;
                        }
                        elements.nodes.push(elements.node(edge.source, edge.source_label, edge.source_types));
                        elements.nodes.push(elements.node(edge.target, edge.target_label, edge.target_types));
                        elements.edges.push(elements.edge(edge));
                    });
                });
            if (!elements.all) {
                elements.all = function() {
                    return elements.nodes.concat(elements.edges);
                }
                elements.empty = function() {
                    newElements = {
                        edges : [],
                        edgeMap : elements.edgeMap,
                        edge : elements.edge,
                        nodes : [],
                        nodeMap : elements.nodeMap,
                        node : elements.node,
                        all : function() {
                            return newElements.nodes.concat(newElements.edges);
                        }
                    }
                    return newElements;
                }
            }
            return p;
        }
        return links;
    }]);

    app.factory("getSummary",['listify',function(listify) {
        var summaryProperties = [
            'http://www.w3.org/2004/02/skos/core#definition',
            'http://purl.org/dc/terms/abstract',
            'http://purl.org/dc/terms/description',
            'http://purl.org/dc/terms/summary',
            'http://www.w3.org/2000/01/rdf-schema#comment',
            "http://purl.obolibrary.org/obo/IAO_0000115",
            'http://www.w3.org/ns/prov#value',
            'http://semanticscience.org/resource/hasValue'
        ];
        function getSummary(ldEntity) {
            console.log(ldEntity);
            for (var i=0; i<summaryProperties.length; i++) {
                if (ldEntity[summaryProperties[i]] != null) {
                    var summary =  listify(ldEntity[summaryProperties[i]])[0];
                    if (summary['@value']) summary = summary['@value'];
                    return summary;
                }
            }
        };
        return getSummary;
    }]);
                
    app.filter('kglink', function() {
        return function(uri, view) {
            uri = window.encodeURIComponent(uri);
            var result = ROOT_URL+"about?";
            if (view) result += 'view='+view+'&';
            result += 'uri='+uri;
            return result;
        };
    });
    
    app.directive("explore", ["$http", 'links', '$timeout', '$mdSidenav', "resolveEntity", 'getSummary',
                              function($http, links, $timeout, $mdSidenav, resolveEntity, getSummary) {
	return {
            scope: {
                elements : "=?",
                style : "=?",
                layout : "=?",
                title : "=?",
                start: "@?"
            },
            templateUrl: ROOT_URL+'static/html/explore.html',
	    restrict: "E",
            link: function(scope, element, attrs) {
                scope.toggleSidebar = function() {
                    $mdSidenav("explore").toggle();
                }
                $mdSidenav("explore").close();
                scope.selectedEntities = null;
                scope.searchText = null;
                scope.ROOT_URL = ROOT_URL;

                scope.searchTextChange = function(text) {
                    scope.searchText = text;
                }

                scope.selectedItemChange = function(entity) {
                    scope.selectedEntities = [entity];
                }

                scope.remove = function() {
                    var selected = scope.cy.$(':selected');
                    scope.cy.remove(selected);
                    var selectedMap = {};
                    selected.forEach(function(d) {
                        selectedMap[d.id()] = d;
                    });
                    scope.elements.nodes = scope.elements.nodes.filter(function(d) {
                        return selectedMap[d.data.id] == null;
                    });
                    scope.elements.edges = scope.elements.edges.filter(function(d) {
                        return selectedMap[d.data.id] == null
                            && selectedMap[d.data.source] == null
                            && selectedMap[d.data.target] == null ;
                    });
                    
                }

                scope.loading = [];
                function incomingOutgoing(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        console.log(scope.probThreshold);
                        links(e, 'incoming', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            return links(e, 'outgoing', scope.elements, render, scope.probThreshold, scope.numSearch);
                        }).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }
                scope.incomingOutgoing = incomingOutgoing;
                scope.add = function() {
                    if (scope.selectedEntities) {
                        incomingOutgoing(scope.selectedEntities.map(function(d) { return d.node}))
                    } else if (scope.searchText && scope.searchText.length > 3) {
                        resolveEntity(scope.searchText).then(function (entities) {
                            incomingOutgoing(entities.map(function(d) { return d.node}))
                        });
                    }
                }

                scope.incoming = function(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        links(e, 'incoming', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }
                
                scope.outgoing = function(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        links(e, 'outgoing', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }
                
                if (!scope.style) {
                    scope.style = cytoscape.stylesheet()
                        .selector('node')
                        .css({
                            'min-zoomed-font-size': 8,
                            'text-valign': 'center',
                            'border-width': 0,
                            'cursor': 'pointer',
                            'color' : 'white',
                            'font-size': 'mapData(rank,0,1,8,24)',
//                            'font-size' : '8px',
                            'text-wrap': 'wrap',
                            'text-max-width': 'mapData(rank,0,1,100,300)',
                            //'text-outline-width' : 3,
                            //'text-outline-opacity' : 1,
                            'text-background-opacity' : 1,
                            'text-background-shape' : 'roundrectangle',
                            'text-background-padding' : '1px',
                            'width': 'mapData(rank,0,1,100,300)',
                            'height': 'mapData(rank,0,1,30,90)',
                        })
                        .selector('node[color]')
                        .css({
                            'background-color': 'data(color)',
                            'text-background-color': 'data(color)',
                            'shape': 'data(shape)',
                            //'text-outline-color' : 'data(color)',
                            //'border-color': 'data(linecolor)',
//                            'height': 'data(size)',
//                            'width': 'data(size)',
                        })
                        .selector('node[label]')
                        .css({
                            'content': 'data(label)',
                        })
                        .selector('edge')
                        .css({
                            'width':'data(width)',
                            'target-arrow-shape': 'data(shape)',
                            'curve-style' : 'bezier',
                            'target-arrow-color': 'data(color)',
                            'line-color': 'data(color)'
                        })
                        .selector('edge[label]')
                        .css({
                            'font-size' : '6px',
                            'source-text-offset': '0.5em',
                            'text-wrap':'wrap',
                            'text-max-width':'5em',
                            'source-label': 'data(label)',
                        })
                        .selector('edge[negation]')
                        .css({
                            'line-style':'dotted',
                        })
                        .selector(':selected')
                        .css({
                            //'background-color': '#D8D8D8',
                            'border-color': '#b2d7fd',
                            'border-width': 2,
                            'line-color': '#b2d7fd',
                            'target-arrow-color': '#b2d7fd',
                            'source-arrow-color': '#b2d7fd',
                            'opacity':1,
                        })
                        .selector('.highlighted')
                        .css({
                            'background-color': '#000000',
                            'line-color': '#000000',
                            'target-arrow-color': '#000000',
                            'transition-property': 'background-color, line-color, target-arrow-color, height, width',
                            'transition-duration': '0.5s'
                        })
                        .selector(':locked')
                        .css({
                            'background-color': '#7f8c8d'
                        })
                        .selector('.faded')
                        .css({
                            'opacity': 0.25,
                            'text-opacity': 0
                        })
                }
                
                /* 
                 * CYTOSCAPE IMPLEMENTATION
                 */
                scope.neighborhood = [];
                if (!scope.layout)
                    scope.layout = {
                        name: 'cose-bilkent',
                        animate: false,
                        //randomize: true,
                        nodeDimensionsIncludeLabels: true,
                        //fit: false,
                        //padding: [20,20,20,20],
                        idealEdgeLength: 60,
                        //circle: true,
                        //concentric: function(){ 
                            //var rank = scope.pageRank.rank(this);
                            //console.log(this, rank, this.degree());
                            //return scope.pageRank.ordinal[rank];
                            //this.indegree() + this.outdegree();
                            //return this.degree() * 10;
                        //},
                        //maxSimulationTime: parseInt(scope.numLayout) * 1000
                    };

                scope.selected = [];
                
                scope.cy = cytoscape({
                    container: $(element).find('.graph'),
                    style: scope.style,
                    elements: [] ,
                    hideLabelsOnViewport: true ,
                    ready: function(){
                        scope.cy = cy = this;
                        cy.boxSelectionEnabled(true);
                        
                        // Clicking on whitespace removes all CSS changes
                        cy.on('vclick', function(e){
                            if( e.cyTarget === cy ){
                                cy.elements().removeClass('faded');
                                cy.elements().removeClass("highlighted");
                                scope.bfsrun = false;
                                scope.neighborhood = [];
                            }
                        });

                        // When an element is selected
                        cy.on('select unselect', function(e){
                            scope.$apply(function() {
                                scope.selected =  scope.cy.$(':selected');
                                scope.selected.forEach(function(d) {
                                    updateDetails(d.data());
                                });
                                console.log(scope.selected.map(function(d) {return d.data()}));
                            });
                        });
                    }
                });

                function updateDetails(data) {
                    data.loading = 0;
                    data.loaded = 0;
                    if (! data.label) {
                        data.loading += 1;
                        $http.get('about',{ params: {uri:data.uri,view:'label'}})
                            .then(function(response) {
                                data.label = response.data;
                                data.loaded += 1;
                                if (update) render();
                            });
                    }
                    function updateTypes(data) {
                        if (data['@type'] == null) return;
                        data.types = data['@type'].map(function(d) {
                            var result = {
                                uri: d,
                            };
                            console.log(d);
                            data.loading += 1;
                            $http.get(ROOT_URL+'about',{ params: {uri:d,view:'label'}})
                                .then(function(response) {
                                    result.label = response.data;
                                    data.loaded += 1; 
                                });
                            return result;
                        });
                    }
                    if (! data.described) {
                        data.described = true;
                        data.loading += 1;
                        $http.get(ROOT_URL+'about',{ params: {uri:data.uri,view:'describe'}, responseType:'json'})
                            .then(function(response) {
                                response.data.forEach(function(x) {
                                    if (x['@id'] == data.uri) {
                                        $.extend(data, x);
                                    }
                                });
                                data.summary = getSummary(data);
                                updateTypes(data);
                                data.loaded += 1;
                                render();
                            });
                    } else {
                        if (data.types == null)
                            updateTypes(data);
                        data.summary = getSummary(data);
                        if (data.summary && data.summary['@value']) data.summary = data.summary['@value'];
                    }
                }


                /* 
                 * OPTIONS
                 */
                scope.showLabel = true;
                scope.bfsrun = false;
                scope.numSearch = 1;
                scope.numLayout = 20;
                scope.probThreshold = BASE_RATE;
                scope.found = -1;
                scope.once = false;
                scope.query = "none";     
                scope.filter = {
                    "customNode": {
                        "activator": true,
                        "inhibitor": true,
                        "protein": true,
                        "disease": true,
                        "drug": true,
                        "undef": true
                    },
                    "customEdge": {
                        "activation": true,
                        "inhibition": true,
                        "association": true,
                        "reaction": true,
                        "cleavage": true,
                        "interaction": true
                    }
                }
                

                /*
                 * HELPER FUNCTIONS
                 */
                
                // Error Handling
                scope.handleError = function(data,status, headers, config) {
                    scope.error = true;
                    scope.loading = false;
                };
                // Returns a list of the requested attribute of the selected nodes.
                scope.getSelected = function(attr) {
                    if (!scope.cy) return [];
                    var selected = scope.cy.$('node:selected');
                    var query = [];
                    selected.nodes().each(function(i,d) { query.push(d.data[attr]); });
                    return query;
                };

                /*
                 * NODE FUNCTIONS
                 */

                // Gets the details of a node by opening the uri in a new window.
                scope.getDetails = function(query) {
                    query.forEach(function(uri) { window.open(ROOT_URL+'about?uri='+uri); });
                };
                // Shows BFS animation starting from selected nodes
                scope.showBFS = function(query) {
                    scope.bfsrun = true;
                    query.forEach(function(id) {
                        cy.elements().removeClass("highlighted");
                        var root = "#" + id;
                        var bfs = cy.elements().bfs(root, function(){}, true);
                        var i = 0;
                        var highlightNextEle = function(){
                            bfs.path[i].addClass('highlighted');
                            bfs.path[i].removeClass('faded');
                            if( i < bfs.path.length - 1){
                                i++;
                                if (scope.bfsrun) {
                                    setTimeout(highlightNextEle, 50);
                                } else { i = bfs.path.length; }
                            }
                        };
                        highlightNextEle();
                    });
                };
                // Lock/unlock the selected elements
                scope.lock = function(query, lock) {
                    query.forEach(function(id) {
                        var node = "#" + id;
                        if (lock) { cy.$(node).lock(); }
                        else { cy.$(node).unlock(); }
                    });
                }
                if (!scope.elements) scope.elements = {};


                function updateCentrality() {
                    var nodes = scope.cy.nodes();
                    var pr = nodes.betweennessCentrality({weight:function(edge) {
                        return edge.data("probability");
                    }} );
                    nodes.forEach(function(node) {
                        var rank = pr.betweennessNormalized(node);
                        node.data("rank",rank);
                        console.log(node.data(), rank);
                    });
                }
                
                scope.update = update;
                function render() {
                    elements = scope.elements.all();
                    var eles = scope.cy.add(elements);
                    updateCentrality();
                    scope.cy.style().update();
                }
                function update() {
                    var elements = [];
                    if (scope.elements && scope.elements.all) {
                        scope.thisElement = scope.cy.$id(scope.start);
                        elements = scope.elements.all();
                        var eles = scope.cy.add(elements);
                        //setTimeout(function(){
                        updateCentrality();
                        scope.cy.style().update();
                        scope.cy.layout(scope.layout).run();
                        //    scope.$apply(function(){ scope.loading = false; });
                        //}, 1000);
                        scope.cy.resize();
                    }
                };

                
                //scope.$watchCollection('elements.edges', update);
                
                if (scope.start) {
                    incomingOutgoing([scope.start]);
                }
            }
        }
    }]);

    /*
     * DBpedia service
     * Handles SPARQL queries and defines facet configurations.
     */
    app.service('instanceFacetService', function(FacetResultHandler, $http) {

        /* Public API */

        // Get the results from DBpedia based on the facet selections.
        this.getResults = getResults;
        // Get the facet definitions.
        this.getFacets = getFacets;
        // Get the facet options.
        this.getFacetOptions = getFacetOptions;

        /* Implementation */

        // Facet definitions
        // 'facetId' is a "friendly" identifier for the facet,
        //  and should be unique within the set of facets.
        // 'predicate' is the property that defines the facet (can also be
        //  a property path, for example).
        // 'name' is the title of the facet to show to the user.
        // If 'enabled' is not true, the facet will be disabled by default.
        var facets = [
            // Text search facet for names
            {
                facetId: 'label',
                predicate:'(rdfs:label|skos:prefLabel|skos:altLabel|dc:title|<http://xmlns.com/foaf/0.1/name>|<http://schema.org/name>)',
                enabled: true,
                name: 'Label',
                type: 'text'
            },
            // Text search facet for descriptions
            {
                facetId: 'description',
                predicate:'(rdfs:comment|skos:definition|dc:description|dc:abstract)',
                enabled: true,
                name: 'Description',
                type: 'text'
            },
            // Text search facet for types
            {
                facetId: 'type',
                predicate:'rdf:type/rdfs:subClassOf*',
                specifier: 'FILTER (!ISBLANK(?value) && !strstarts(str(?value), "bnode:") )',
                preferredLang: "en",
                enabled: true,
                type: 'basic',
                name: 'Type'
            }
        ];

        $http.get(ROOT_URL+'about',{ params: {uri:NODE_URI,view:'constraints'}, responseType:'json'})
            .then(function(response) {
                response.data.forEach(function (d) {
                    d.name = d.propertyLabel;
                    if (d.rangeLabel && d.name.indexOf(d.rangeLabel) == -1)
                        d.name += " " + d.rangeLabel;
                    d.facetId = d.property;
                    if (d.range)
                        d.facetId += " " + d.range;
                    d.predicate = '<'+d.property+'>';
                    d.enabled = true;
                    d.preferredLang = "en";
                    d.type = "basic";
                    facets.push(d);
                });
            });

        var endpointUrl = ROOT_URL+'sparql';

        // We are building a faceted search for classes.
        var rdfClass = '<'+NODE_URI+'>';

        // The facet configuration also accept a 'constraint' option.
        // The value should be a valid SPARQL pattern.
        // One could restrict the results further, e.g., to writers in the
        // science fiction genre by using the 'constraint' option:
        //
        // var constraint = '?id <http://dbpedia.org/ontology/genre> <http://dbpedia.org/resource/Science_fiction> .';
        //
        // Note that the variable representing a result in the constraint should be "?id".
        //
        // 'rdfClass' is just a shorthand constraint for '?id a <rdfClass> .'
        // Both rdfClass and constraint are optional, but you should define at least
        // one of them, or you might get bad results when there are no facet selections.
        var facetOptions = {
            endpointUrl: endpointUrl, // required
            rdfClass: rdfClass, // optional
            constraint: 'FILTER (!ISBLANK(?id))\n\
FILTER ( !strstarts(str(?id), "bnode:") )\n\
',
            preferredLang : 'en' // required
        };

        var prefixes =
            ' PREFIX owl: <http://www.w3.org/2002/07/owl#>\n' +
            ' PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n' +
            ' PREFIX dc: <http://purl.org/dc/terms/>\n' +
            ' PREFIX bds: <http://www.bigdata.com/rdf/search#>\n' +
            ' PREFIX foaf: <http://xmlns.com/foaf/0.1/>\n' +
            ' PREFIX skos: <http://www.w3.org/2004/02/skos/core#>\n\n';

        // This is the result query, with <RESULT_SET> as a placeholder for
        // the result set subquery that is formed from the facet selections.
        // The variable names used in the query will be the property names of
        // the reusulting mapped objects.
        // Note that ?id is the variable used for the result resource here,
        // as in the constraint option.
        // Variable names with a '__' (double underscore) in them will results in
        // an object. I.e. here ?work__id, ?work__label, and ?work__link will be
        // combined into an object:
        // writer.work = { id: '[work id]', label: '[work label]', link: '[work link]' }
        var queryTemplate =
        ' SELECT * WHERE {\n' +
        '  <RESULT_SET> \n' +
        '  OPTIONAL { \n'+
        '   ?id rdfs:label|skos:prefLabel|dc:title|<http://xmlns.com/foaf/0.1/name>|<http://schema.org/name> ?label . \n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   ?id skos:definition|rdfs:comment|dc:description:dc:abstract|dc:summary ?description . \n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   ?id foaf:depiction|<http://schema.org/image> ?depiction . \n' +
        '  }\n' +
        '  OPTIONAL { \n' +
        '   ?id rdf:type/rdfs:subClassOf* ?type__id . \n' +
        '   FILTER (!ISBLANK(?type__id) && !strstarts(str(?type__id), "bnode:") )' +
        '   OPTIONAL { \n' +
        '    ?type__id rdfs:label ?type__label . \n' +
        '   }\n' +
        '  }\n' +
        ' }';

        var resultOptions = {
            prefixes: prefixes, // required if the queryTemplate uses prefixes
            queryTemplate: queryTemplate, // required
            resultsPerPage: 10, // optional (default is 10)
            pagesPerQuery: 1, // optional (default is 1)
            paging: true // optional (default is true), if true, enable paging of the results
        };

        // FacetResultHandler is a service that queries the endpoint with
        // the query and maps the results to objects.
        var resultHandler = new FacetResultHandler(endpointUrl, resultOptions);

        // This function receives the facet selections from the controller
        // and gets the results from DBpedia.
        // Returns a promise.
        function getResults(facetSelections) {
            // If there are variables used in the constraint option (see above),
            // you can also give getResults another parameter that is the sort
            // order of the results (as a valid SPARQL ORDER BY sequence, e.g. "?id").
            // The results are sorted by URI (?id) by default.
            return resultHandler.getResults(facetSelections).then(function(pager) {
                // We'll also query for the total number of results, and load the
                // first page of results.
                return pager.getTotalCount().then(function(count) {
                    pager.totalCount = count;
                    return pager.getPage(0);
                }).then(function() {
                    return pager;
                });
            });
        }

        // Getter for the facet definitions.
        function getFacets() {
            return facets;
        }

        // Getter for the facet options.
        function getFacetOptions() {
            return facetOptions;
        }
    });

    /*
     * The controller.
     */
    app.controller('InstanceFacetController', function($scope, FacetHandler, instanceFacetService, facetUrlStateHandlerService, getLabel, $http) {
        var vm = this;

        var updateId = 0;

        // page is the current page of results.
        vm.page = [];
        vm.pageNo = 0;
        vm.getPage = getPage;
        vm.makeArray = makeArray;
        vm.getLabel = getLabel;

        vm.disableFacets = disableFacets;

        // Listen for the facet events
        // This event is triggered when a facet's selection has changed.
        $scope.$on('sf-facet-constraints', updateResults);
        // This is the initial configuration event
        var initListener = $scope.$on('sf-initial-constraints', function(event, cons) {
            updateResults(event, cons);
            // Only listen once, then unregister
            initListener();
        });

        // Get the facet configurations from dbpediaService.
        vm.facets = instanceFacetService.getFacets();
        // Initialize the facet handler
        vm.handler = new FacetHandler(getFacetOptions());

        // Disable the facets while results are being retrieved.
        function disableFacets() {
            return vm.isLoadingResults;
        }

        // Setup the FacetHandler options.
        function getFacetOptions() {
            var options = instanceFacetService.getFacetOptions();
            options.scope = $scope;

            // Get initial facet values from URL parameters (refresh/bookmark) using facetUrlStateHandlerService.
            options.initialState = facetUrlStateHandlerService.getFacetValuesFromUrlParams();
            return options;
        }


        // Get results based on facet selections (each time the selections change).
        function updateResults(event, facetSelections) {
            // As the facets are not locked while the results are loading,
            // this function may be called again before the results have been
            // retrieved. This creates a race condition where the later call
            // may return before the first one, which leads to an inconsistent
            // state once the first returns. To avoid this we'll have a counter
            // that is incremented each time update is called, and we'll abort
            // the update if the counter has been incremented before it finishes.
            var uid = ++updateId;
            // As the user can also change the page via pagination, and introduce
            // a race condition that way, we'll want to discard any pending
            // page changes if a facet value changes. So set a boolean flag for
            // this purpose.
            vm.lock = true;
            // This variable is used to disable page selection, and display the
            // spinner animation.
            vm.isLoadingResults = true;

            // Update the URL parameters based on facet selections
            facetUrlStateHandlerService.updateUrlParams(facetSelections);

            // The dbpediaService returns a (promise of a) pager object.
            return instanceFacetService.getResults(facetSelections)
            .then(function(pager) {
                if (uid === updateId) {
                    vm.pager = pager;
                    vm.totalCount = pager.totalCount;
                    vm.pageNo = 1;
                    getPage(uid).then(function() {
                        vm.lock = false;
                        return vm.page;
                    });
                }
            });
        }

        // Get a page of mapped objects.
        // Angular-UI pagination handles the page number changes.
        function getPage(uid) {
            vm.isLoadingResults = true;
            // Get the page.
            // (The pager uses 0-indexed pages, whereas Angular-UI pagination uses 1-indexed pages).
            return vm.pager.getPage(vm.pageNo-1).then(function(page) {
                // Check if it's ok to change the page
                if (!vm.lock || (uid === updateId)) {
                    vm.page = page;
                    vm.page.forEach(function(d) {
                        $http.get(ROOT_URL+'about',{ params: {uri:d.id,view:'label'}})
                            .then(function(response) {
                                d.label = response.data;
                            });
                        $http.get(ROOT_URL+'about',{ params: {uri:d.id,view:'summary'}, responseType:'json'})
                            .then(function(response) {
                                d.summary = response.data;
                            });
                        d.type.forEach(function(type) {
                            getLabel(type.id).then(function(d) { type.label = d});
                        });
                    });
                    vm.isLoadingResults = false;
                }
            }).catch(function(error) {
                vm.error = error;
                vm.isLoadingResults = false;
            });
        }

        function makeArray(val) {
            return angular.isArray(val) ? val : [val];
        }
    });

    app.service('makeID',function() {
        var ID = function () {
            // Math.random should be unique because of its seeding algorithm.
            // Convert it to base 36 (numbers + letters), and grab the first 9 characters
            // after the decimal.
            return Math.random().toString(36).substr(2, 10);
        };
        return ID;
    });

    app.service("resolveURI", function() {
        function resolveURI(uri, context) {
            if (context[uri]) {
                return resolveURI(context[uri]);
            } else if (uri.indexOf(':') != -1) {
                var i = s.indexOf(':');
                var parts = [s.slice(0,i), s.slice(i+1)];
                var prefix = parts[0];
                var local = parts[1];
                if (context[prefix]) {
                    c = context[prefix];
                    if (c['@id']) c = c['@id'];
                    return resolveURI(c+local);
                }
            } else if (context['@vocab']) {
                return context['@vocab'] + uri;
            }
            return uri;
        }
        return resolveURI;
    });
    
    /*
     * The controller - New Instance.
     */
    app.controller('NewInstanceController', function($scope, $http, makeID, Nanopub, resolveURI) {
        var vm = this;
        var np_id = makeID();
        // let contextString = "";
        vm.resolveURI = resolveURI;
        vm.submit = function() {
            vm.nanopub['@graph'].isAbout = {"@id": vm.instance['@id']};
            var entityURI = resolveURI(vm.instance['@id'],vm.nanopub['@context']);
            Nanopub.save(vm.nanopub).then(function() {
                window.location.href = ROOT_URL+'about?uri='+window.encodeURIComponent(entityURI);
            });
        }

        
        vm.nanopub = {
            "@context" : {
                "@vocab": LOD_PREFIX+'/',
                "@base": LOD_PREFIX+'/',
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "whyis" : "http://vocab.rpi.edu/whyis/",
                "np" : "http://www.nanopub.org/nschema#",
                "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
                'sio' : 'http://semanticscience.org/resource/',
                'isAbout' : { "@id" : 'sio:isAbout', "@type" : "@uri"},
                'dc' : 'http://purl.org/dc/terms/',
                'prov' : 'http://www.w3.org/ns/prov#',
                'references' : {"@id" : 'dc:references', "@type": "@uri"},
                'quoted from' : {"@id" : 'prov:wasQuotedFrom', "@type": "@uri"},
                'derived from' : {"@id" : 'prov:wasDerivedFrom', "@type": "@uri"},
                'label' : {"@id" : 'rdfs:label', "@type": "xsd:string"},
                'description' : {'@id' : 'dc:description', '@type': 'xsd:string'}
            },
            "@id" : "urn:"+np_id,
            "@graph" : {
                "@id" : "urn:"+np_id,
                "@type": "np:Nanopublication",
                "np:hasAssertion" : {
                    "@id" : "urn:"+np_id+"_assertion",
                    "@type" : "np:Assertion",
                    "@graph" : {
                        "@id": makeID(),
                        "@type" : [NODE_URI],
                        'label' : {
                            "@value": ""
                        },
                        'description' : {
                            "@value": ""
                        }
                    }
                },
                "np:hasProvenance" : {
                    "@id" : "urn:"+np_id+"_provenance",
                    "@type" : "np:Provenance",
                    "@graph" : {
                        "@id": "urn:"+np_id+"_assertion",
                        "references": [],
                        'quoted from' : [],
                        'derived from' : []
                    }
                },
                "np:hasPublicationInfo" : {
                    "@id" : "urn:"+np_id+"_pubinfo",
                    "@type" : "np:PublicationInfo",
                    "@graph" : {
                        "@id": "urn:"+np_id,
                    }
                }
            }
        };
        vm.instance = vm.nanopub['@graph']['np:hasAssertion']['@graph'];
        vm.provenance = vm.nanopub['@graph']['np:hasProvenance']['@graph'];

        function populateContext(constraint) {
            if (!vm.nanopub["@context"][constraint.propertyLabel]) {
                vm.nanopub["@context"][constraint.propertyLabel] = [];
            }
            var newProperty = {};
            newProperty["@superClass"] = constraint.superClass;
            newProperty["@range"] = constraint.range;
            newProperty["@rangeLabel"] = constraint.rangeLabel;
            newProperty["@extent"] = constraint.extent;
            newProperty["@cardinality"] = constraint.cardinality;
            newProperty["@class"] = constraint.class;
            newProperty["@property"] = constraint.property;
            newProperty["@propertyLabel"] = constraint.propertyLabel;
            newProperty["@propertyType"] = constraint.propertyType;
            vm.nanopub["@context"][constraint.propertyLabel].push(newProperty);
        }

        function populateJsonObject(currentObject) {
            if (currentObject["@id"]) {
                $http.get(ROOT_URL+"about",{ 'params': { "view":"constraints", "uri":currentObject["@type"]},'resultType': 'json' })
                .then(function(data) {
                    let constraints = data.data;
                    for (constraint of constraints) {
                        populateContext(constraint);
                        if ((!currentObject[constraint.propertyLabel])) {
                            currentObject[constraint.propertyLabel] = [];
                        }
                        if (constraint.propertyType === "http://www.w3.org/2002/07/owl#ObjectProperty") {
                            let newObject = {};
                            newObject["@id"] = makeID();
                            newObject["@type"] = constraint.range;
                            populateJsonObject(newObject);
                            currentObject[constraint.propertyLabel].push(newObject);
                        } else {
                            let newObject = {};
                            newObject["@value"] = "";
                            currentObject[constraint.propertyLabel].push(newObject);
                        }
                    }
                    return;
                }, function(error){
                    console.log(error);
                    return;
                });
            } else {
                return;
            }
        }
        
        populateJsonObject(vm.instance);

        $scope.globalContext = vm.nanopub['@context'];
    });
    
    /*
     * New Directive for new_instance_view.html and edit_instance_view.html
     */
    app.directive('globalJsonContext',  function(){
        return {
            restrict: 'EA',
            scope: false,
            link: function(data){
                console.log('context is: ', data.globalContext );
            }
        }
    });

    /*
     * The controller - Edit Instance.
     */
    
    app.controller('EditInstanceController', function($scope, $http, makeID, Nanopub, resolveURI) {
        var vm = this;
        var np_id = makeID();
        // let contextString = "";
        vm.resolveURI = resolveURI;
        vm.submit = function() {
            vm.nanopub['@graph'].isAbout = {"@id": vm.instance['@id']};
            var entityURI = resolveURI(vm.instance['@id'],vm.nanopub['@context']);
            Nanopub.save(vm.nanopub).then(function() {
                window.location.href = ROOT_URL+'about?uri='+window.encodeURIComponent(entityURI);
            });
        }

        
        vm.nanopub = {
            "@context" : {
                "@vocab": LOD_PREFIX+'/',
                "@base": LOD_PREFIX+'/',
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "whyis" : "http://vocab.rpi.edu/whyis/",
                "np" : "http://www.nanopub.org/nschema#",
                "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
                'sio' : 'http://semanticscience.org/resource/',
                'isAbout' : { "@id" : 'sio:isAbout', "@type" : "@uri"},
                'dc' : 'http://purl.org/dc/terms/',
                'prov' : 'http://www.w3.org/ns/prov#',
                'references' : {"@id" : 'dc:references', "@type": "@uri"},
                'quoted from' : {"@id" : 'prov:wasQuotedFrom', "@type": "@uri"},
                'derived from' : {"@id" : 'prov:wasDerivedFrom', "@type": "@uri"},
                'label' : {"@id" : 'rdfs:label', "@type": "xsd:string"},
                'description' : {'@id' : 'dc:description', '@type': 'xsd:string'}
            },
            "@id" : "urn:"+np_id,
            "@graph" : {
                "@id" : "urn:"+np_id,
                "@type": "np:Nanopublication",
                "np:hasAssertion" : {
                    "@id" : "urn:"+np_id+"_assertion",
                    "@type" : "np:Assertion",
                    "@graph" : {
                        "@id": makeID(),
                        "@type" : [NODE_URI],
                        'label' : [],
                        'description' : []
                    }
                },
                "np:hasProvenance" : {
                    "@id" : "urn:"+np_id+"_provenance",
                    "@type" : "np:Provenance",
                    "@graph" : {
                        "@id": "urn:"+np_id+"_assertion",
                        "references": [],
                        'quoted from' : [],
                        'derived from' : []
                    }
                },
                "np:hasPublicationInfo" : {
                    "@id" : "urn:"+np_id+"_pubinfo",
                    "@type" : "np:PublicationInfo",
                    "@graph" : {
                        "@id": "urn:"+np_id,
                    }
                }
            }
        };

        vm.instance = vm.nanopub['@graph']['np:hasAssertion']['@graph'];
        vm.provenance = vm.nanopub['@graph']['np:hasProvenance']['@graph'];
        
        //get the constrainsts for the class
        $http.get(ROOT_URL+'about',{ 'params': { "view":"constraints", "uri":NODE_URI },'resultType': 'json' })
            .then(function(data) {
                let constraints = data.data;
                
                console.log('class constraints:', constraints);
                contextObject = {}
                for (constraint of constraints) {
                    vm.nanopub["@context"][constraint.superClass] = {};
                    vm.nanopub["@context"][constraint.superClass]["@id"] = constraint.property;
                    vm.nanopub["@context"][constraint.superClass]["@type"] = constraint.range;
                    vm.nanopub["@context"][constraint.superClass]["@extent"] = constraint.extent;
                    vm.nanopub["@context"][constraint.superClass]["@cardinality"] = constraint.cardinality;
                    vm.nanopub["@context"][constraint.superClass]["@propertyType"] = constraint.propertyType;
                    vm.nanopub["@context"][constraint.superClass]["@propertyLabel"] = constraint.propertyLabel;
                    vm.instance[constraint.superClass] = {};
                    //vm.instance[constraint.superClass]["@id"] = constraint.property;
                    vm.instance[constraint.superClass]["@type"] = constraint.range;
                    vm.instance[constraint.superClass]["@extent"] = constraint.extent;
                    vm.instance[constraint.superClass]["@cardinality"] = constraint.cardinality;
                    vm.instance[constraint.superClass]["@propertyType"] = constraint.propertyType;
                    vm.instance[constraint.superClass]["@propertyLabel"] = constraint.propertyLabel;
                }
        });
        $scope.context = vm.nanopub['@context'];

    });
    
    angular.bootstrap(document, ['App']);

});
