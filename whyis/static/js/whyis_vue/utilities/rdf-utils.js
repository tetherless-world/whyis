/**
 * RDF and Linked Data utilities
 * @module utilities/rdf-utils
 */

/**
 * Convert a value to an array if it isn't already
 * @param {*} x - The value to listify
 * @returns {Array} The value as an array
 * @example
 * listify([1, 2, 3]) // [1, 2, 3]
 * listify('single') // ['single']
 * listify(null) // [null]
 */
export function listify(x) {
    if (x && x.forEach) {
        return x;
    } else {
        return [x];
    }
}

/**
 * Summary properties in order of preference for extracting descriptions
 * @constant
 */
export const SUMMARY_PROPERTIES = [
    'http://www.w3.org/2004/02/skos/core#definition',
    'http://purl.org/dc/terms/abstract',
    'http://purl.org/dc/terms/description',
    'http://purl.org/dc/terms/summary',
    'http://www.w3.org/2000/01/rdf-schema#comment',
    'http://purl.obolibrary.org/obo/IAO_0000115',
    'http://www.w3.org/ns/prov#value',
    'http://semanticscience.org/resource/hasValue'
];

/**
 * Extract a summary/description from a Linked Data entity
 * Checks properties in order of preference and returns the first found
 * @param {Object} ldEntity - The Linked Data entity object
 * @returns {string|undefined} The summary text or undefined if none found
 * @example
 * const entity = {
 *   'http://purl.org/dc/terms/description': [{ '@value': 'A description' }]
 * };
 * getSummary(entity) // 'A description'
 */
export function getSummary(ldEntity) {
    if (!ldEntity) return undefined;
    
    for (let i = 0; i < SUMMARY_PROPERTIES.length; i++) {
        const prop = SUMMARY_PROPERTIES[i];
        if (ldEntity[prop] != null) {
            let summary = listify(ldEntity[prop])[0];
            if (summary && summary['@value']) {
                summary = summary['@value'];
            }
            return summary;
        }
    }
    
    return undefined;
}

/**
 * Get summary property URIs
 * @returns {Array<string>} Array of summary property URIs
 */
export function getSummaryProperties() {
    return [...SUMMARY_PROPERTIES];
}

export default {
    listify,
    getSummary,
    getSummaryProperties,
    SUMMARY_PROPERTIES
};
