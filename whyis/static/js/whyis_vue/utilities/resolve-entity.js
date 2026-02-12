/**
 * Entity resolution utilities for search and autocomplete
 * @module utilities/resolve-entity
 */

import axios from 'axios';

/**
 * Resolve entities by searching for them
 * @param {string} query - The search query
 * @param {string} [type] - Optional type filter for entities
 * @param {string} [rootUrl] - The root URL for the API (defaults to window.ROOT_URL)
 * @returns {Promise<Array>} A promise that resolves to an array of matching entities
 * @example
 * resolveEntity('test')
 *   .then(entities => console.log(entities))
 */
export async function resolveEntity(query, type, rootUrl) {
    const ROOT_URL = rootUrl || (typeof window !== 'undefined' ? window.ROOT_URL : '');
    
    const params = {
        view: 'resolve',
        term: query + "*"
    };
    
    if (type !== undefined) {
        params.type = type;
    }
    
    try {
        const response = await axios.get(ROOT_URL, {
            params,
            responseType: 'json'
        });
        
        // Process the response data
        return (response.data || []).map(hit => {
            // Add lowercase value for filtering
            hit.value = hit.label ? hit.label.toLowerCase() : '';
            return hit;
        });
    } catch (error) {
        console.error('Error resolving entities:', error);
        return [];
    }
}

export default {
    resolveEntity
};
