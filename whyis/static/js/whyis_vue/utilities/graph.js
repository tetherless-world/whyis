/**
 * RDF Graph and Resource management
 * @module utilities/graph
 */

import axios from 'axios';
import { listify } from './rdf-utils';

/**
 * Resource class for managing RDF resources in a graph
 */
class Resource {
    /**
     * Create a Resource
     * @param {string} uri - The URI of the resource
     * @param {Graph} graph - The graph this resource belongs to
     */
    constructor(uri, graph) {
        this.uri = uri;
        this.graph = graph;
        this.po = {}; // predicate-object map
    }

    /**
     * Get all values for a predicate
     * @param {string} p - The predicate URI
     * @returns {Array} Array of values
     */
    values(p) {
        if (!this.po[p]) this.po[p] = [];
        return this.po[p];
    }

    /**
     * Check if resource has values for a predicate
     * @param {string} p - The predicate URI
     * @returns {boolean} True if has values
     */
    has(p) {
        return !!(this.po[p] && this.po[p].length > 0);
    }

    /**
     * Get the first value for a predicate
     * @param {string} p - The predicate URI
     * @returns {*} The first value or undefined
     */
    value(p) {
        if (this.has(p)) {
            return this.values(p)[0];
        }
        return undefined;
    }

    /**
     * Add a value for a predicate
     * @param {string} p - The predicate URI
     * @param {*} o - The value to add
     */
    add(p, o) {
        this.values(p).push(o);
    }

    /**
     * Set (replace) values for a predicate
     * @param {string} p - The predicate URI
     * @param {*} o - The value to set
     */
    set(p, o) {
        this.po[p] = [o];
    }

    /**
     * Delete all values for a predicate
     * @param {string} p - The predicate URI
     */
    del(p) {
        delete this.po[p];
    }

    /**
     * Fetch resource data from its URI
     * @returns {Promise} Promise resolving to the HTTP response
     */
    async get() {
        return axios.get(this.uri, {
            headers: { 'Accept': 'application/ld+json;q=1' }
        });
    }

    /**
     * Convert resource to JSON-LD format
     * @returns {Object} JSON-LD representation
     */
    toJSON() {
        const result = { '@id': this.uri };
        
        Object.keys(this.po).forEach(key => {
            const values = listify(this.values(key)).map(value => {
                if (value && value.uri) {
                    return { '@id': value.uri };
                } else if (value && value.toISOString) {
                    // Handle Date objects
                    return {
                        '@value': value.toISOString(),
                        '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
                    };
                } else {
                    return value;
                }
            });
            result[key] = values;
        });
        
        return result;
    }
}

/**
 * Graph class for managing RDF graphs
 */
class Graph extends Array {
    constructor() {
        super();
        this.resourceMap = {};
        this.ofTypeMap = {};
        
        // Type converters for JSON-LD data
        this.converters = {
            'http://www.w3.org/2001/XMLSchema#dateTime': (v) => new Date(v)
        };
    }

    /**
     * Get or create a resource in the graph
     * @param {string} uri - The resource URI
     * @returns {Resource} The resource
     */
    resource(uri) {
        if (!this.resourceMap[uri]) {
            this.resourceMap[uri] = new Resource(uri, this);
            this.push(this.resourceMap[uri]);
        }
        return this.resourceMap[uri];
    }

    /**
     * Get all resources of a specific type
     * @param {string} type - The type URI
     * @returns {Array<Resource>} Array of resources
     */
    ofType(type) {
        if (this.ofTypeMap[type] == null) {
            this.ofTypeMap[type] = [];
        }
        return this.ofTypeMap[type];
    }

    /**
     * Merge JSON-LD data into the graph
     * @param {Object|Array} json - JSON-LD data to merge
     */
    merge(json) {
        if (json == null) return;

        // Handle single resource
        if (json['@id']) {
            const resource = this.resource(json['@id']);
            
            Object.keys(json).forEach(key => {
                if (key === '@id' || key === '@graph') return;
                
                if (key === '@type') {
                    listify(json[key]).forEach(type => {
                        resource.add('@type', this.resource(type));
                        this.ofType(type).push(resource);
                    });
                } else {
                    listify(json[key]).forEach(o => {
                        let value = o;
                        
                        // Handle resource references
                        if (o && o['@id']) {
                            value = this.resource(o['@id']);
                        }
                        // Handle literals with type conversion
                        else if (o && o['@value']) {
                            if (o['@type'] && this.converters[o['@type']]) {
                                value = this.converters[o['@type']](o['@value']);
                            } else {
                                value = o['@value'];
                            }
                        }
                        
                        resource.add(key, value);
                    });
                }
            });
        }

        // Handle @graph property
        if (json['@graph']) {
            json['@graph'].forEach(item => this.merge(item));
        }

        // Handle array of resources
        if (json.forEach && !json['@id']) {
            json.forEach(item => this.merge(item));
        }
    }

    /**
     * Export graph to JSON-LD format
     * @returns {Object} JSON-LD representation with @graph
     */
    toJSON() {
        return {
            '@graph': Array.from(this).map(resource => resource.toJSON())
        };
    }
}

/**
 * Create a new Graph instance
 * @returns {Graph} A new graph instance
 * @example
 * const graph = createGraph();
 * const resource = graph.resource('http://example.org/resource/1');
 * resource.add('http://www.w3.org/2000/01/rdf-schema#label', 'My Resource');
 */
export function createGraph() {
    return new Graph();
}

export { Graph, Resource };

export default {
    createGraph,
    Graph,
    Resource
};
