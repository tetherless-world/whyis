/**
 * Knowledge graph links service
 * Handles fetching and managing graph nodes and edges
 * @module utilities/kg-links
 */

import axios from 'axios';

/**
 * Get node feature based on types
 * @param {string} feature - Feature name (shape, color, etc.)
 * @param {Array} types - Array of type URIs
 * @returns {*} Feature value
 */
function getNodeFeature(feature, types) {
    // This would need to be implemented based on configuration
    // For now, return default values
    const defaults = {
        'shape': 'ellipse',
        'color': '#666',
        'border-color': '#000',
        'background-color': '#fff'
    };
    return defaults[feature];
}

/**
 * Get edge feature based on types
 * @param {string} feature - Feature name
 * @param {Array} types - Array of type URIs
 * @returns {*} Feature value
 */
function getEdgeFeature(feature, types) {
    const defaults = {
        'shape': 'bezier',
        'color': '#999',
        'label': true
    };
    return defaults[feature];
}

/**
 * Create a links service for knowledge graph exploration
 * @param {string} [rootUrl] - The root URL for API calls
 * @returns {Object} Links service
 */
export function createLinksService(rootUrl) {
    const ROOT_URL = rootUrl || (typeof window !== 'undefined' ? window.ROOT_URL : '/');

    /**
     * Fetch links (edges) for an entity
     * @param {string} entity - Entity URI
     * @param {string} view - View type ('incoming' or 'outgoing')
     * @param {Object} elements - Graph elements object
     * @param {Function} [update] - Optional update callback
     * @param {number} [maxP=0.93] - Maximum probability threshold
     * @param {number} [distance=1] - Distance parameter
     * @returns {Promise} Promise resolving when links are fetched
     */
    async function links(entity, view, elements, update, maxP, distance) {
        if (distance == null) distance = 1;
        if (maxP == null) maxP = 0.93;

        // Initialize nodes structure if not present
        if (!elements.nodes) {
            elements.nodes = [];
        }
        if (!elements.nodeMap) {
            elements.nodeMap = {};
        }
        if (!elements.node) {
            /**
             * Create or get a node
             * @param {string} uri - Node URI
             * @param {string} label - Node label
             * @param {Array} types - Node types
             * @returns {Object} Node object
             */
            elements.node = function(uri, label, types) {
                if (!elements.nodeMap[uri]) {
                    elements.nodeMap[uri] = {
                        group: 'nodes',
                        data: { uri, id: uri, label }
                    };
                    const nodeEntry = elements.nodeMap[uri];

                    function processTypes() {
                        if (nodeEntry.data['@type']) {
                            const types = nodeEntry.data['@type'];
                            nodeEntry.classes = types.join(' ');
                            if (!nodeEntry.data.shape)
                                nodeEntry.data.shape = getNodeFeature('shape', types);
                            if (!nodeEntry.data.color)
                                nodeEntry.data.color = getNodeFeature('color', types);
                            if (!nodeEntry.data.borderColor)
                                nodeEntry.data.borderColor = getNodeFeature('border-color', types);
                            if (!nodeEntry.data.backgroundColor)
                                nodeEntry.data.backgroundColor = getNodeFeature('background-color', types);
                        }
                    }

                    if (types) {
                        nodeEntry.data['@type'] = types;
                        processTypes();
                    } else {
                        nodeEntry.data.described = true;
                        // Fetch node description
                        axios.get(`${ROOT_URL}about`, {
                            params: { uri, view: 'describe' },
                            responseType: 'json'
                        }).then(response => {
                            if (response.data && response.data.forEach) {
                                response.data.forEach(x => {
                                    if (x['@id'] === uri) {
                                        Object.assign(nodeEntry.data, x);
                                        processTypes();
                                    }
                                });
                            }
                            if (update) update();
                        }).catch(err => {
                            console.error('Error fetching node description:', err);
                        });
                    }

                    if (!nodeEntry.data.label) {
                        // Fetch node label
                        axios.get(`${ROOT_URL}about`, {
                            params: { uri, view: 'label' }
                        }).then(response => {
                            nodeEntry.data.label = response.data;
                            if (update) update();
                        }).catch(err => {
                            console.error('Error fetching node label:', err);
                        });
                    }
                }
                return elements.nodeMap[uri];
            };
        }

        // Initialize edges if not present (always initialize to ensure it's available)
        if (!elements.edges) {
            elements.edges = [];
        }
        if (!elements.edgeMap) {
            elements.edgeMap = {};
        }
        if (!elements.edge) {
            /**
             * Create or get an edge
             * @param {Object} edge - Edge data
             * @returns {Object} Edge object
             */
            elements.edge = function(edge) {
                const edgeKey = [edge.source, edge.link, edge.target].join(' ');
                edge.uri = edge.link;

                if (!elements.edgeMap[edgeKey]) {
                    elements.edgeMap[edgeKey] = {
                        group: 'edges',
                        data: edge
                    };
                    const edgeEntry = elements.edgeMap[edgeKey];
                    edgeEntry.id = edgeKey;

                    if (edgeEntry.data['link_types']) {
                        const types = edgeEntry.data['link_types'];
                        edgeEntry['@types'] = types;
                        edgeEntry.classes = types.join(' ');
                        if (!edgeEntry.data.shape)
                            edgeEntry.data.shape = getEdgeFeature('shape', types);
                        if (!edgeEntry.data.color)
                            edgeEntry.data.color = getEdgeFeature('color', types);
                        if (getEdgeFeature('label', types) && types.length > 0) {
                            edgeEntry.data.label = types[0].label;
                        }
                    }

                    if (edgeEntry.data.zscore) {
                        edgeEntry.data.width = Math.abs(edgeEntry.data.zscore) + 1;
                    } else {
                        edgeEntry.data.width = 1 + (edgeEntry.data.probability || 0);
                    }

                    if (edgeEntry.data.zscore < 0) {
                        edgeEntry.data.negation = true;
                    }
                }
                return elements.edgeMap[edgeKey];
            };
        }

        // Fetch links from API
        try {
            const response = await axios.get(`${ROOT_URL}about`, {
                params: { uri: entity, view },
                responseType: 'json'
            });

            if (response.data && response.data.forEach) {
                response.data.forEach(edge => {
                    if (edge.probability < maxP) {
                        console.log(edge.probability, maxP, 'skipping', edge);
                        return;
                    }
                    elements.nodes.push(elements.node(edge.source, edge.source_label, edge.source_types));
                    elements.nodes.push(elements.node(edge.target, edge.target_label, edge.target_types));
                    elements.edges.push(elements.edge(edge));
                });
            }
        } catch (error) {
            console.error('Error fetching links:', error);
            throw error;
        }

        // Add utility methods
        if (!elements.all) {
            elements.all = function() {
                return elements.nodes.concat(elements.edges);
            };

            elements.empty = function() {
                const newElements = {
                    edges: [],
                    edgeMap: elements.edgeMap,
                    edge: elements.edge,
                    nodes: [],
                    nodeMap: elements.nodeMap,
                    node: elements.node,
                    all: function() {
                        return newElements.nodes.concat(newElements.edges);
                    }
                };
                return newElements;
            };
        }
    }

    return links;
}

/**
 * Create empty graph elements structure
 * @returns {Object} Empty elements structure
 */
export function createGraphElements() {
    return {
        nodes: [],
        edges: [],
        nodeMap: {},
        edgeMap: {}
    };
}

export default {
    createLinksService,
    createGraphElements
};
