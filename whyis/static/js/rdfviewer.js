RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type";
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label";
FOAF_NAME = "http://xmlns.com/foaf/0.1/name";
DC_TITLE = "http://purl.org/dc/elements/1.1/title";
DCT_TITLE = "http://purl.org/dc/terms/title";
SKOS_PREFLABEL = "http://www.w3.org/2004/02/skos/core#prefLabel";

d3.selection.prototype.moveToFront = function() {
  return this.each(function(){
    this.parentNode.appendChild(this);
  });
};

function getLocale() {
    if ( navigator ) {
        if ( navigator.language ) {
            return navigator.language;
        }
        else if ( navigator.browserLanguage ) {
            return navigator.browserLanguage;
        }
        else if ( navigator.systemLanguage ) {
            return navigator.systemLanguage;
        }
        else if ( navigator.userLanguage ) {
            return navigator.userLanguage;
        }
    } else return 'en';
}
var locale = getLocale();

$.extend({
  getUrlVars: function(){
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
      hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  },
  getUrlVar: function(name){
    return $.getUrlVars()[name];
  }
});

function polygonIntersect(c, d, a, b) {
  var x1 = c[0], x2 = d[0], x3 = a[0], x4 = b[0],
      y1 = c[1], y2 = d[1], y3 = a[1], y4 = b[1],
      x13 = x1 - x3,
      x21 = x2 - x1,
      x43 = x4 - x3,
      y13 = y1 - y3,
      y21 = y2 - y1,
      y43 = y4 - y3,
      ua = (x43 * y13 - y43 * x13) / (y43 * x21 - x43 * y21);
  return [x1 + ua * x21, y1 + ua * y21];
}

function pointInBox(rect, b) {
    return b.x > rect.x && b.x < rect.x + rect.width &&
        b.y > rect.y && b.y < rect.y + rect.height;
}

function pointInLine(a,c,d) {
    return a[0] >= Math.min(c[0],d[0]) &&
        a[0] <= Math.max(c[0],d[0]) &&
        a[1] >= Math.min(c[1],d[1]) &&
        a[1] <= Math.max(c[1],d[1]);
}

function edgePoint(rect, a, b) {
    comparePoint = a
    if (pointInBox(rect,b))
        comparePoint = b;
    
    lines = [[[rect.x,rect.y], // top horizontal
              [rect.x+rect.width,rect.y]],
             [[rect.x,rect.y+rect.height], // bottom horizontal
              [rect.x+rect.width,rect.y+rect.height]],
             [[rect.x,rect.y], // left vertical
              [rect.x,rect.y+rect.height]],
             [[rect.x+rect.width,rect.y], // right vertical
              [rect.x+rect.width,rect.y+rect.height]]];
    intersects = lines.map(function(x) {
        return polygonIntersect(x[0],x[1],a,b);
    });
    if (pointInLine(intersects[0],a,b)  && 
        intersects[0][0] >= rect.x &&
        intersects[0][0] <= rect.x + rect.width) {
        return intersects[0];
    } else if (pointInLine(intersects[1],a,b) && 
               intersects[1][0] >= rect.x &&
               intersects[1][0] <= rect.x + rect.width) {
        return intersects[1];
    } else if (pointInLine(intersects[2],a,b) && 
               intersects[2][1] >= rect.y &&
               intersects[2][1] <= rect.y + rect.height) {
        return intersects[2];
    } else if (pointInLine(intersects[3],a,b) && 
               intersects[3][1] >= rect.y &&
               intersects[3][1] <= rect.y + rect.height) {
        return intersects[3];
    } else return null;
}

function makeCenteredBox(node) {
    var box = {};
    box.x = node.x - node.width / 2;
    box.y = node.y - node.height / 2;
    box.width = node.width;
    box.height = node.height;
    return box;
}

var OWL = "http://www.w3.org/2002/07/owl#";
var RDFS = "http://www.w3.org/2000/01/rdf-schema#";
var XSD = "http://www.w3.org/2001/XMLSchema#";

var extraLabels = {}
extraLabels[RDFS+"subClassOf"] = "sub-class of";
extraLabels[OWL+"equivalentClass"] = "equivalent class";
extraLabels[OWL+"inverseOf"] = "inverse of";
extraLabels[OWL+"ObjectProperty"] = "Object Property";
extraLabels[OWL+"DatatypeProperty"] = "Data Property";
extraLabels[XSD+"length"] = "length";
extraLabels[XSD+"minLength"] = "minLength";
extraLabels[XSD+"maxLength"] = "maxLength";
extraLabels[XSD+"pattern"] = "pattern";
extraLabels[XSD+"langRange"] = "langRange";
extraLabels[XSD+"minInclusive"] = "<=";
extraLabels[XSD+"maxInclusive"] = ">=";
extraLabels[XSD+"minExclusive"] = "<";
extraLabels[XSD+"maxExclusive"] = ">";

function conditionalize(fn, condition) {
    function wrapper() {
        return fn.apply(null,arguments);
    }
    wrapper.onlyif = condition;
    return wrapper;
}

var decorators = {
    anchor: function (callback) { 
        return function(d) { 
            var label = callback(d); 
            label = '<a href="/about?uri='+d.uri+'">'+label+"</a>";
            return label;
        }; 
    }
}
var labelers = [
    conditionalize(function(resource) {
        var label = ""
        var datatype = resource.value(OWL+'onDatatype');
        var restrictions = resource.relations[OWL+'withRestrictions'].map(function(r) {
            return d3.entries(r.attribs).filter(function(po) {
                return extraLabels[po.key] != null;
            }).map(function(po) {
                return extraLabels[po.key]+po.value[0];
            }).join("");
        });
        label = label + getLabel(datatype)+'['+restrictions.join(", ")+']';
        //console.log("facet:",label, resource);
        return label;
    },
    function(resource) {
        return resource.uri 
            && (resource.types.map(function(d){return d.uri}).indexOf(RDFS+'Datatype') != -1) 
            && (resource.value(OWL+'onDatatype'));
    }),
    conditionalize(function(resource) {
        var label = ""
        if (resource.relations[OWL+'intersectionOf']) {
            label = label + resource.relations[OWL+'intersectionOf'].map(getLabel).join(" and ");
        } else if (resource.relations[OWL+'unionOf']) {
            label = label + resource.relations[OWL+'unionOf'].map(getLabel).join(" or ");
        } else if (resource.relations[OWL+'complementOf']) {
            label = label + "cannot be "+resource.relations[OWL+'complementOf'].map(getLabel).join(", nor ");
        } else if (resource.relations[OWL+'datatypeComplementOf']) {
            label = label + "cannot be "+resource.relations[OWL+'datatypeComplementOf'].map(getLabel).join(", nor ");
        } else if (resource.relations[OWL+'oneOf']) {
            label = label + "is one of {"+ resource.relations[OWL+'oneOf'].map(getLabel).join(", ")+"}";
        } else if (resource.value(OWL+'onDatatype')) {
            console.warn("not handling datatype",resource);
        } else {
            console.warn("Not handling class",resource);
        }
        if (resource.types.map(function(d){return d.uri}).indexOf(RDFS+'Datatype') != -1) {
            console.warn("Datatype:",resource);
        }
        if (label.length > 0) label = "("+label+")";
        return label;
    },
    function(resource) {
        return resource.uri && resource.uri.indexOf("_:") == 0 
            && (resource.types.map(function(d){return d.uri}).indexOf(OWL+'Class') != -1
                || resource.types.map(function(d){return d.uri}).indexOf(RDFS+'Datatype') != -1)
    }),
    conditionalize(function(resource) {
        var label = getLabel(resource.relations[OWL+'onProperty'][0]);

        if (resource.value(OWL+'hasValue')) {
            label = label + " value " + getLabel(resource.value(OWL+'hasValue'));
        } else if (resource.value(OWL+'someValuesFrom')) {
            label = label + " some " + getLabel(resource.value(OWL+'someValuesFrom'));
        } else if (resource.value(OWL+'allValuesFrom')) {
            var l =  getLabel(resource.value(OWL+'allValuesFrom'));
            //console.log(l, resource.value(OWL+'allValuesFrom'));
            label = label + " only " + l;
        } else if (resource.value(OWL+'hasSelf')) {
            label = label + " self " ;
        } else if (resource.value(OWL+'minCardinality')) {
            label = label + " min " + resource.value(OWL+'minCardinality');
        } else if (resource.value(OWL+'minQualifiedCardinality')) {
            label = label + " min " + resource.value(OWL+'minQualifiedCardinality');
            if (resource.value(OWL+'onClass'))
                label = label + " " + getLabel(resource.value(OWL+'onClass'));
            else if (resource.value(OWL+'onDataRange'))
                label = label + " " + getLabel(resource.value(OWL+'onDataRange'));
        } else if (resource.value(OWL+'maxCardinality')) {
            label = label + " max " + resource.value(OWL+'maxCardinality');
        } else if (resource.value(OWL+'maxQualifiedCardinality')) {
            label = label + " max " + resource.value(OWL+'maxQualifiedCardinality');
            if (resource.value(OWL+'onClass'))
                label = label + " " + getLabel(resource.value(OWL+'onClass'));
            else if (resource.value(OWL+'onDataRange'))
                label = label + " " + getLabel(resource.value(OWL+'onDataRange'));
        } else if (resource.value(OWL+'maxCardinality')) {
            label = label + " max " + resource.value(OWL+'maxCardinality');
        } else if (resource.value(OWL+'cardinality')) {
            label = label + " exactly " + resource.value(OWL+'cardinality');
        } else if (resource.value(OWL+'qualifiedCardinality')) {
            label = label + " exactly " + resource.value(OWL+'qualifiedCardinality');
            if (resource.value(OWL+'onClass'))
                label = label + " " + getLabel(resource.value(OWL+'onClass'));
            else if (resource.value(OWL+'onDataRange'))
                label = label + " " + getLabel(resource.value(OWL+'onDataRange'));
        } else {
            console.warn("not handling restriction",resource);
        }

        return label;
    },
    function(resource) {
        return resource.uri && resource.type == 'resource' 
            && resource.types.map(function(d){return d.uri}).indexOf(OWL+'Restriction') != -1
    }),
    conditionalize(decorators.anchor(function(d) {
        var ext = d.uri.split('.');
        ext = ext[ext.length-1];
        if (ext == 'ico') {
            return '<img src="'+d.uri+'" alt="'+label+'"/>'
        }
        return '<img width="100" src="'+d.uri+'" alt="'+d.label+'"/>';
    }),
    function(d) {
        if (!d.uri) return false;
        var ext = d.uri.split('.');
        ext = ext[ext.length-1];
        return $.inArray(ext, ['jpeg','jpg','png','gif','ico']) != -1;
    }),
    conditionalize(decorators.anchor(function (d) {
        if (d.label) return d.label;
        else return d;
    }),
    function(d) {return true})
]

function getLabel(d) {
    var mylabels = labelers.filter(function(fn) {return fn.onlyif(d)});
    var result =  mylabels[0](d);
    //console.log(d, mylabels, result);
    return result;
}

function getGravatar(uri) {
    var hash = md5(uri);
    return "http://www.gravatar.com/avatar/"+hash+"?d=identicon&r=g%s=20"
}

function Graph() {
    this.resources = {},
    this.nodes = [];
    this.edges = [];
    this.predicates = [];
    this.entities = [];
    
}
Graph.prototype.makeLink = function(source, target,arrow) {
    link = {};
    link.source = source;
    link.target = target;
    link.value = 1;
    link.display = true;
    link.arrow = arrow;
    this.edges.push(link);
    return link;
}

Graph.prototype.getSP = function(s, p) {
    var result = this.resources[s.uri+' '+p.uri];
    if (result == null) {
        result = {};
        result.width = 0;
        result.type = 'predicate';
        result.display = true;
        result.subject = s;
        result.predicate = p;
        result.objects = [];
        result.uri = s.uri+' '+p.uri;
        result.isPredicate = false;
        this.resources[result.uri] = result;
        link = this.makeLink(s,result,false);
        result.links = [];
        s.links.push(link);
        result.links.push(link);
    }
    return result;
}

Graph.prototype.getResource = function(uri) {
    var result = this.resources[uri];
    if (result == null) {
        result = {};
        result.value = function(uri) {
            var results = result.relations[uri];
            if (results == null || results.length == 0) results = result.attribs[uri];
            if (results == null || results.length == 0) return null;
            return results[0];
        };
        result.width = 0;
        result.type = 'resource';
        result.types = [];
        result.display = false;
        result.attribs = {};
        result.relations = {};
        result.objectOf = [];
        result.uri = uri;
        result.label = ' ';
        result.depth = -1;
        result.localPart = result.uri.split("#").filter(function(d) {return d.length > 0});
        result.localPart = result.localPart[result.localPart.length-1];
        result.localPart = result.localPart.split("/").filter(function(d) {return d.length > 0});
        result.localPart = result.localPart[result.localPart.length-1];
        result.label = result.localPart;
        result.labeled = false;
        if (extraLabels[uri]) {
            result.label = extraLabels[uri];
            result.labeled = true;
        }
        result.links = [];
        result.isPredicate = false;
        this.resources[uri] = result;
    }
    return result;
}

function squashLists(d) {
    var lists = {};
    var resources = {};

    d3.entries(d).forEach(function(subj){
        if (subj.value['http://www.w3.org/1999/02/22-rdf-syntax-ns#first']) {
            lists[subj.key] = subj.value;
        }
        else resources[subj.key] = subj.value;
    });

    var result = {};

    d3.entries(resources).forEach(function(subj) {

        if (subj.key == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')
            return;
        result[subj.key] = {};
        d3.entries(subj.value).forEach(function(pred) {
            var list = [];
            result[subj.key][pred.key] = list;
            pred.value.forEach(function(obj) {
                if (lists[obj.value]) {
                    var o = obj.value;
                    //console.log(o);
                    while (o) {
                        o = lists[o];
                        //console.log(o);
                        list.push(o['http://www.w3.org/1999/02/22-rdf-syntax-ns#first'][0])
                        o = o['http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'][0].value;
                        //console.log(o);
                        if (o == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil')
                            o = null;
                    }
                } else {
                    list.push(obj);
                }
            })
        })
    })
    //console.log(result);
    return result;
}

function listify(x) {
    if (!x.forEach) x = [x];
    var result = [];
    x.forEach(function(a) {
        if (a['@list']) result = result.concat(a);
        else result.push(a);
    });
    return result;
};


Graph.prototype.load = function(d) {
    var g = this
    //d = squashLists(d);
    d.forEach(function(s) {
        if (s['@graph']) {
            g.load(s['@graph']);
        }
        subj = s['@id'];
        d3.entries(s).forEach(function(pred) {
            if (pred.key == '@id' || pred.key == '@graph' || pred.key == '@context') return;
            
            listify(pred.value).forEach(function(obj) {
                var resource = g.getResource(subj);
                resource.display = true;
                if (pred.key == RDF_TYPE) {
                    resource.types.push(g.getResource(obj['@id']));
                    return;
                }
                else if (pred.key == '@type') {
                    if (obj['@id']) obj = obj['@id'];
                    resource.types.push(g.getResource(obj));
                    return;
                }
                var predicate = g.getResource(pred.key);
                predicate.isPredicate = true;
                if (obj["@value"] || !obj['@id']) {
                    // if (obj['@lang'] != null) {
                    //     if (locale.lastIndexOf(obj.lang, 0) === 0) {
                    //     } else {
                    //         //console.log(obj.lang);
                    //         return;
                    //     }
                    // }
                    if (obj['@value']) obj = obj['@value'];
                    if (pred.key == RDFS_LABEL && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else if (pred.key == FOAF_NAME && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else if (pred.key == DC_TITLE && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else if (pred.key == DCT_TITLE && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else if (pred.key == SKOS_PREFLABEL && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else if (pred.key == "http://semanticscience.org/resource/hasValue" && !resource.labeled) {
                        resource.label = obj;
                        resource.labeled = true;
                    } else {
                        if (resource.attribs[predicate.uri] == null) {
                            resource.attribs[predicate.uri] = [];
                        }
                        resource.attribs[predicate.uri].push(obj);
                    }
                } else {
                    sp = g.getSP(resource, predicate);
                    o = g.getResource(obj['@id']);
                    if ((obj['@id'] == null || obj['@id'].startsWith("bnode:")) && o.label == o.uri) {
                        o.label = ' ';
                        o.labeled = true;
                    }
                    sp.objects.push(o);
                    o.display = true;
                    o.objectOf.push(sp);
                    var link = g.makeLink(sp,o,true);
                    sp.links.push(link);
                    if (resource.relations[predicate.uri] == null) {
                        resource.relations[predicate.uri] = [];
                    }
                    resource.relations[predicate.uri].push(o);
                }
            })
        })
    });
    var q = d3.queue(2);
    var labels = d3.map();
    d3.values(g.resources).filter(function(resource){
        return (resource.type == "resource") && !resource.labeled;
    }).forEach(function(resource) {
        if (!labels.has(resource.uri)) {
            labels.set(resource.uri, []);
        }
        labels.get(resource.uri).push(resource);
    });

    labels.each(function(resources, uri) {
        q.defer(function(callback) {
            d3.text("/about?view=label&uri="+encodeURIComponent(uri), function(label) {
                resources.forEach(function(r) {
                    r.label = label;
                });
                callback(null);
            })
        });
    });
    function hideSP(sp) {
        sp.display=false;
        sp.links.forEach(function(l){l.display=false});
        sp.predicate=true;
    }
    d3.values(g.resources).filter(function(resource){
        return (resource.type == 'resource' 
                && resource.types.map(function(d){return d.uri}).indexOf(OWL+'Restriction') != -1) ||
               (resource.uri.indexOf("_:") == 0 && resource.types
                && (resource.types.map(function(d){return d.uri}).indexOf(OWL+'Class') != -1
                    || resource.types.map(function(d){return d.uri}).indexOf(OWL+'Datatype') != -1))
    }).forEach(function(resource){
        resource.objectOf.forEach(function(sp){
            resource.display = false;
            if (sp.subject.attribs[sp.predicate.uri] == null) {
                sp.subject.attribs[sp.predicate.uri] = [];
            }
            sp.subject.attribs[sp.predicate.uri].push(resource);
            //console.log(sp);
        })
    })

    d3.values(g.resources).filter(function(resource){
        var result = resource.type == "predicate";
        if (result) {
            result = resource.objects.reduce(function(prev,o) {
                return d3.keys(o.attribs).length == 0 &&
                    d3.keys(o.relations).length == 0 &&
                    o.types.length == 0 &&
                    d3.keys(o.objectOf).length == 1 && prev;
            },result);
        }
        return result;
    }).forEach(function(resource) {
        resource.subject.attribs[resource.predicate.uri] = resource.objects;
        resource.display = false;
        resource.objects.forEach(function(o) {
            o.display = false;
        });
        resource.links.forEach(function(l) {
            l.display = false;
        });
    });
    
    g.predicates = d3.values(g.resources).filter(function(node) {
        if (node.type == 'predicate' && !node.isPredicate) {
            node.display = node.display && node.subject.display;
            return node.display;
        } else return false;
    }).filter(function(node){
        node.display = node.display && node.objects.reduce(function(prev, o) {
            return prev || o.display;
        },false);
        return node.display;
    });
    g.predicates.forEach(function(p) {
        p.label = p.predicate.label;
    });

    g.nodes = d3.values(g.resources).filter(function(node) {
        return (!node.isPredicate && node.display);
    });
    
    g.entities = d3.values(g.resources).filter(function(node) {
        return (node.type == 'resource' && !node.isPredicate && node.display);
    }).sort(function(a,b) {
        return a.objectOf.length - b.objectOf.length;
    });
    
    //console.log(g.entities)    
    g.edges = d3.values(g.edges).filter(function(l) {
        return l.display && l.source.display && l.target.display;
    });
    return q;
}

function loader(url, doLoad) {
    $.getJSON(url, doLoad);
}
    
function loadGraph(url, fn) {
    function doLoad(d) {
        graph = new Graph();
        graph.load(d);
        fn(graph);
    }
    loader(url, doLoad);
}

function makeNodeSVG(entities, vis, nodeWidth, graph, renderer) {
    var node = vis.selectAll("g.node")
        .data(entities)
        .enter();

    node = node.append("svg:foreignObject")
        .attr('width',nodeWidth)
        .attr('height','1000')
        .attr("cursor", "pointer");
    
    node.append("xhtml:body").attr('xmlns',"http://www.w3.org/1999/xhtml");
    
    var body = node.selectAll("body")
        //.style("max-width",nodeWidth+"px")
    var resource = body//.append("div")
        //.style("max-width","100%")
        //.style("display","block")
        .append("table")
        .attr("class",function(d) {
            var classes = d.types.map(function(d){ return d.localPart;})
            return "resource "+classes.join(" ");
        })
        .style("table-layout","fixed");
    var titles = resource.append("xhtml:tr")
        .append("xhtml:th")
        .style("word-wrap","break-word")
        .style("max-width",nodeWidth+"px")
        .attr("class","title")
        .attr("colspan","2")
        .html(function(d) { return getLabel(d); })
    var types = resource.append("xhtml:tr")
        .append("xhtml:td")
        .attr("colspan","2")
        .attr("class","type")
        .html(function(d) {
            var typeLabels = d.types.map(function(t) {
                if (t.label != ' ')
                    return '<a href="/about?uri='+t.uri+'">'+t.label+'</a>';
                else return '<a href="/about?uri='+t.uri+'">'+t.localPart+'</a>';
            });
            if (typeLabels.length > 0) {
                return "a&nbsp;" + typeLabels.join(", ");
            } else {
                return "";
            }
        })
        .attr("href",function(d) { return d.uri});
    
    var attrs = resource.selectAll("td.attr")
        .data(function(d) {
            var entries = d3.entries(d.attribs);
            return entries;
        }).enter()
        .append("xhtml:tr");
    attrs.append("xhtml:td")
        .attr("class","attrName")
        .text(function(d) {
            predicate = graph.getResource(d.key);
            if (predicate.label != ' ')
                return predicate.label+":";
            else return predicate.localPart+":";
        });
    attrs.append("xhtml:td")
        .style("word-wrap","break-word")
        .style("max-width",nodeWidth+"px")
        //.style("width","60%")
        .html(function(d) {
            return d.value.map(function(d) {
                if (d.type == "resource") {
                    return getLabel(d);
                } else return d;
            }).join(", ");
        });
    node.selectAll("img").on("load", renderer);
    return node;
}

function makePredicateSVG(predicates, vis) {
    var result = vis.selectAll("g.predicate")
        .data(predicates)
        .enter()
        .append("svg:text")
        .attr("class","link")
        .attr("text-anchor","middle")
        .attr("alignment-baseline","middle")
        .attr("x", function(d) { return d.x; })
        .attr("y", function(d) { return d.y; })
        .text(function(d){
            if (d.predicate.label != ' ') d.predicate.label;
             else return d.predicate.localPart;
            return d.predicate.label;
        })
        .attr("cursor", "pointer")
        .attr("xlink:href",function(d) { return d.predicate.uri;});
    return result;
}

function makeLinkSVG(edges, vis) {
    var result = {};
    result.link = vis.selectAll("line.link")
        .data(edges)
        .enter().append("svg:g").attr("class", "link");

    result.link.append("svg:line")
        .attr("class", "link")
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
    
    result.arrowhead = result.link.filter(function(d) {
        return d.arrow;
    })
        .append("svg:polygon")
        .attr("class", "arrowhead")
        .attr("transform",function(d) {
            angle = Math.atan2(d.y2-d.y1, d.x2-d.x1);
            return "rotate("+angle+", "+d.x2+", "+d.y2+")";
        })
        .attr("points", function(d) {
            //angle = (d.y2-d.y1)/(d.x2-d.x1);
            return [[d.x2,d.y2].join(","),
                    [d.x2-3,d.y2+8].join(","),
                    [d.x2+3,d.y2+8].join(",")].join(" ");
        });
    return result;
}

var layout = {};

function uuid4() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
    

layout.dagre = function(nodes, predicates, links, rankDir) {
    if (!rankDir) rankDir = 'lr';
    // Create a new directed graph 
    var g = new dagre.graphlib.Graph({ multigraph: true});
    
    // Set an object for the graph label
    g.setGraph({});
    
    // Default to assigning a new object as a label for each new edge.
    g.setDefaultEdgeLabel(function() { return {}; });

    nodes.forEach(function(node) {
        if (!node.id) {
            if (node.type == 'resource') {
                node.id = node.uri;
            } else {
                node.id = uuid4();
            }
        }
        g.setNode(node.uri, node);
    });

    predicates.forEach(function(predicate) {
        if (!predicate.id) {
            predicate.id = uuid4();
        }
        g.setNode(predicate.uri, predicate);
    });

    links.forEach(function(link) {
        g.setEdge(link.source.uri, link.target.uri);
    });

    g.graph().nodesep = 20;
    g.graph().ranksep = 20;
    g.graph().rankDir = rankDir;
    //g.graph().align = 'lr';
    //g.graph().ranker = "tight-tree";
    //g.graph().acyclicer = "greedy";
    dagre.layout(g);

    var dimension = 'x',
        down = d3.min,
        up = d3.max;
    switch (rankDir) {
    case 'lr':
        dimension = 'x';
        down = d3.min;
        up = d3.max;
        break;
    case 'lr':
        dimension = 'x';
        down = d3.min;
        up = d3.max;
        break;
    case 'rl':
        dimension = 'x';
        down = d3.max;
        up = d3.min;
        break;
    case 'tb':
        dimension = 'y';
        down = d3.min;
        up = d3.max;
        break;
    case 'bt':
        dimension = 'y';
        down = d3.max;
        up = d3.min;
        break;
    }

    var positions = d3.set(d3.merge([predicates.map(function(x){ return x[dimension]} ),
                                    nodes.map(function(x){ return x[dimension]})]))
        .values().map(parseFloat);
    var scale = d3.scaleThreshold().domain(positions).range(positions);

    predicates.forEach(function(predicate) {
        var subj = predicate.subject[dimension];
        var obj = down(predicate.objects, function(d) { return d[dimension];});
        var extent = d3.extent([subj,obj]);
        if (predicate[dimension] < extent[0] || predicate[dimension] > extent[1])
            predicate[dimension] = scale(d3.mean(extent));
    });
    return g;
}

layout.force = function() {
    function fn(nodes, links, update) {
    force.start();
    }
    fn.force = d3.layout.force();
    fn.force.size([width, height]);
    fn.force.charge(-1000)
        .linkStrength(1)
        .linkDistance(function(d){
            var width = d.source.width/2 + d.target.width/2 + 25;
            return width;
        })
    //.linkDistance(50)
        .gravity(0.05)

    return fn;
}

function rdfview() {
    
    var nodeWidth = 300;
    function fn() {
        var svg = d3.select(this);
        var graph = svg.datum();

        var chart = d3.select(svg.node().parentNode);
        var transMatrix = [1,0,0,1,0,0];
    
        //svg.append("rect").attr("width",10000)
        //    .attr('height',10000)
        //    .attr('fill','white');
        var container = svg.append("g");
        var vis = container.append("g");
        var selector = container.append("rect")
            .attr("class","selector")
            .attr("display","none");


        var zoomed = false;
        // Set up zoom support
        var inner = svg.select("g"),
            zoom = d3.zoom().on("zoom", function() {
                var transform = d3.zoomTransform(svg.node());
                inner.attr("transform", "translate(" + transform.x +","+transform.y + ")" +
                           "scale(" + transform.k + ")");
                zoomed = true;
            })
            .on("start", function() {
                //zoomed = false;
            })
            .on("end", function() {
                if (!zoomed) {
                    //selected = null;
                    //update();
                }
            });

        var links = makeLinkSVG(graph.edges, vis);
        
        var predicates = makePredicateSVG(graph.predicates, vis);
        
        var node = makeNodeSVG(graph.entities, vis, nodeWidth, graph, render);

        var selected = null;
        
        var drag = d3.drag();
        var moved = false;
        drag.on("drag", function(d,i) {
            d.x += d3.event.dx;
            d.y += d3.event.dy;
            update();
            moved = true;
        });
        drag.on("start", function(d) {
            moved = false;
            d3.event.sourceEvent.stopPropagation();
            d3.select(this).classed("dragging", true);
        });
        drag.on("end", function(d) {
            d3.select(this).classed("dragging", false);
            if (!moved) {
                selected = selected == d ? null : d;
                update();
            }
        });

        node.call(drag);
        predicates.call(drag);
        svg.call(zoom);
        
        function update() {
      	    links.link.selectAll("line.link")
                .attr("x1", function(d) {
                    var box = makeCenteredBox(d.source);
                    var ept = edgePoint(box,
                                        [d.source.x,d.source.y],
                                        [d.target.x,d.target.y]);
                    d.x1 = d.source.x;
                    if (ept != null) {
                        d.x1 = ept[0]
                    }
                    return d.x1; 
                })
                .attr("y1", function(d) {
                    var box = makeCenteredBox(d.source);
                    var ept = edgePoint(box,
                                        [d.source.x,d.source.y],
                                        [d.target.x,d.target.y]);
                    d.y1 = d.source.y;
                    if (ept != null) {
                        d.y1 = ept[1]
                    }
                    return d.y1; 
                })
                .attr("x2", function(d) {
                    var box = makeCenteredBox(d.target);
                    var ept = edgePoint(box,
                                        [d.source.x,d.source.y],
                                        [d.target.x,d.target.y]);
                    d.x2 = d.target.x;
                    if (ept != null) {
                        d.x2 = ept[0]
                    }
                    return d.x2; 
                })
                .attr("y2", function(d) { 
                    var box = makeCenteredBox(d.target);
                    var ept = edgePoint(box,
                                        [d.source.x,d.source.y],
                                        [d.target.x,d.target.y]);
                    d.y2 = d.target.y;
                    if (ept != null) {
                        d.y2 = ept[1]
                    }
                    return d.y2; 
                });

            selector.attr("display",selected != null ? null: "none")
                .attr("height",selected != null ? selected.height+2 : 0)
                .attr("width",selected != null ? selected.width+2 : 0)
                .attr("x",selected != null ? selected.x - selected.width/2 - 1 : 0)
                .attr("y",selected != null ? selected.y - selected.height/2 - 1 : 0);

            node.filter(function(d) { return d == selected})
                .each(function(d) { d3.select(this).moveToFront()});
            
            predicates.filter(function(d) { return d == selected})
                .each(function(d) { d3.select(this).moveToFront()});
            
            node.attr("x", function(d) {
                    //d.x = Math.max(d.width/2, Math.min(w-d.width/2, d.x ));
                    return d.x - d.width/2;
                })
                .attr("y", function(d) {
                    //d.y = Math.max(d.height/2, Math.min(h-d.height/2, d.y ));
                    return d.y - d.height/2;
                })
            
            predicates.attr("x", function(d) {
                //d.x = Math.max(10, Math.min(w-10, d.x ));
                return d.x;
            })
                .attr("y", function(d) {
                    //d.y = Math.max(10, Math.min(h-10, d.y ));
                    return d.y;
                })

            links.arrowhead.attr("points", function(d) {
                return [[d.x2,d.y2].join(","),
                        [d.x2-3,d.y2+8].join(","),
                        [d.x2+3,d.y2+8].join(",")].join(" ");
            })
                .attr("transform",function(d) {
                    var angle = Math.atan2(d.y2-d.y1, d.x2-d.x1)*180/Math.PI + 90;
                    return "rotate("+angle+", "+d.x2+", "+d.y2+")";
                });
        }
        
        function render() {
            node
                .attr("height",function(d) {
                    return d.height = this.childNodes[0].childNodes[0].clientHeight+4;
                })
                .attr("width",function(d) {
                    if (d.width == 0 || d.width == nodeWidth) {
                        d.width = this.childNodes[0].childNodes[0].clientWidth+4;
                    }
                    return d.width;
                });
            predicates.each(function(d) {
                d.height = this.clientHeight+4;
                d.width = this.clientWidth+4;
            });
            
            layout.dagre(node.data(), predicates.data(), links.link.data());
            update();
        }
        render();
    }
    fn.nodeWidth = function(x) {
        if (x == null) return nodeWidth;
        else {
            nodeWidth = x;
            return fn;
        }
    }
    return fn;
}
