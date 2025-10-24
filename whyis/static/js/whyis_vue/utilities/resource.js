/**
 * Resource utility for RDF resource manipulation
 * Provides a Resource constructor that creates objects with RDF-specific methods
 * Migrated from Angular.js factory "Resource" in whyis.js
 */

import { listify } from './rdf-utils';

/**
 * Create a Resource object with RDF manipulation methods
 * @param {string} id - The resource ID (@id in JSON-LD)
 * @param {Object} [values] - Initial values for the resource
 * @returns {Object} Resource object with methods for RDF manipulation
 */
export function createResource(id, values) {
    const result = {
        "@id": id
    };

    // Storage for nested resources
    if (!createResource.resources) {
        createResource.resources = {};
    }

    /**
     * Create or get a nested resource
     * @param {string} resourceId - ID of the nested resource
     * @param {Object} [resourceValues] - Values for the nested resource
     * @returns {Object} The nested resource
     */
    result.resource = function(resourceId, resourceValues) {
        let valuesGraph = null;
        if (resourceValues && resourceValues['@graph']) {
            valuesGraph = resourceValues['@graph'];
        }
        
        const nestedResult = createResource(resourceId, resourceValues);

        if (!this.resource.resources[resourceId]) {
            this.resource.resources[resourceId] = nestedResult;
            if (!this['@graph']) this['@graph'] = [];
            this['@graph'].push(this.resource.resources[resourceId]);
        } else {
            const existingResult = this.resource.resources[resourceId];
            if (valuesGraph) {
                valuesGraph.forEach(function(r) {
                    existingResult.resource(r['@id'], r);
                });
            }
        }
        
        return this.resource.resources[resourceId];
    };

    result.resource.resources = {};

    /**
     * Get all values for a predicate as an array
     * @param {string} p - The predicate
     * @returns {Array} Array of values
     */
    result.values = function(p) {
        if (!this[p]) this[p] = [];
        if (!this[p].forEach) this[p] = [this[p]];
        return this[p];
    };

    /**
     * Check if resource has a predicate, optionally with a specific object value
     * @param {string} p - The predicate
     * @param {*} [o] - Optional object value to check for
     * @returns {boolean|Array} True/false if no object specified, array of matches if object specified
     */
    result.has = function(p, o) {
        const hasP = result[p] && (!result[p].forEach || result[p].length > 0);
        if (o == null || hasP == false) {
            return !!hasP;
        } else {
            return result.values(p).filter(function(value) {
                if (o['@id']) {
                    return value['@id'] == o['@id'];
                }
                let compareO = o;
                let compareValue = value;
                if (o['@value']) compareO = o['@value'];
                if (value['@value']) compareValue = value['@value'];
                return compareO == compareValue;
            });
        }
    };

    /**
     * Get the first value for a predicate
     * @param {string} p - The predicate
     * @returns {*} The first value or undefined
     */
    result.value = function(p) {
        if (result.has(p)) {
            return result.values(p)[0];
        }
    };

    /**
     * Add a value to a predicate
     * @param {string} p - The predicate
     * @param {*} o - The object/value to add
     */
    result.add = function(p, o) {
        result.values(p).push(o);
    };

    /**
     * Set a predicate to a single value (replaces existing)
     * @param {string} p - The predicate
     * @param {*} o - The object/value to set
     */
    result.set = function(p, o) {
        this[p] = [o];
    };

    /**
     * Delete a predicate
     * @param {string} p - The predicate
     */
    result.del = function(p) {
        delete this[p];
    };

    // Initialize with provided values
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

/**
 * Default export as a factory function (compatible with Angular pattern)
 */
export default createResource;
