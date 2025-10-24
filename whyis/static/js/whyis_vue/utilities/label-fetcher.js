/**
 * Label fetching and caching utility for resources
 * @module utilities/label-fetcher
 */

import axios from 'axios';

/**
 * Cache for storing fetched labels
 * @private
 */
const labelCache = {};

/**
 * Extract the local part of a URI for display
 * @param {string} uri - The URI to extract from
 * @returns {string} The local part of the URI
 * @private
 */
function extractLocalPart(uri) {
    let localPart = uri.split("#").filter(d => d.length > 0);
    localPart = localPart[localPart.length - 1];
    localPart = localPart.split("/").filter(d => d.length > 0);
    localPart = localPart[localPart.length - 1];
    return localPart;
}

/**
 * Get the label for a URI, with caching
 * @param {string} uri - The URI to get the label for
 * @param {string} [rootUrl] - The root URL for the API (defaults to window.ROOT_URL)
 * @returns {Promise<string>} A promise that resolves to the label
 * @example
 * getLabel('http://example.org/resource/123')
 *   .then(label => console.log(label))
 */
export async function getLabel(uri, rootUrl) {
    const ROOT_URL = rootUrl || (typeof window !== 'undefined' ? window.ROOT_URL : '');
    
    // Check cache first
    if (labelCache[uri]) {
        // If we have a pending promise, return it
        if (labelCache[uri].promise) {
            return labelCache[uri].promise;
        }
        // If we have a cached label, return it as a resolved promise
        if (labelCache[uri].label) {
            return Promise.resolve(labelCache[uri].label);
        }
    }

    // Initialize cache entry with local part as default
    const localPart = extractLocalPart(uri);
    labelCache[uri] = { label: localPart };

    // Fetch the actual label
    const promise = axios.get(`${ROOT_URL}about`, {
        params: { uri, view: 'label' },
        responseType: 'text'
    })
    .then(response => {
        if (response.status === 200 && response.data) {
            labelCache[uri].label = response.data;
        }
        delete labelCache[uri].promise; // Clear the pending promise
        return labelCache[uri].label;
    })
    .catch(error => {
        console.warn(`Failed to fetch label for ${uri}:`, error);
        delete labelCache[uri].promise;
        return labelCache[uri].label; // Return the local part on error
    });

    labelCache[uri].promise = promise;
    return promise;
}

/**
 * Get a label synchronously from the cache (returns local part if not cached)
 * @param {string} uri - The URI to get the label for
 * @returns {string} The cached label or the local part of the URI
 * @example
 * // After calling getLabel() asynchronously first
 * const label = getLabelSync('http://example.org/resource/123')
 */
export function getLabelSync(uri) {
    if (labelCache[uri] && labelCache[uri].label) {
        return labelCache[uri].label;
    }
    return extractLocalPart(uri);
}

/**
 * Clear the label cache
 * @example
 * clearLabelCache() // Clears all cached labels
 */
export function clearLabelCache() {
    Object.keys(labelCache).forEach(key => delete labelCache[key]);
}

/**
 * Check if a label is cached
 * @param {string} uri - The URI to check
 * @returns {boolean} True if the label is cached
 */
export function hasLabel(uri) {
    return !!(labelCache[uri] && labelCache[uri].label !== undefined);
}

/**
 * Vue filter for labels (stateful for reactive updates)
 * Usage in Vue templates: {{ uri | label }}
 * @param {string} uri - The URI to get the label for
 * @returns {string} The label or local part
 */
export function labelFilter(uri) {
    // Trigger async fetch if not cached
    if (!labelCache[uri]) {
        getLabel(uri);
    }
    return getLabelSync(uri);
}

// Make the filter stateful for Vue 2.x
labelFilter.$stateful = true;

export default {
    getLabel,
    getLabelSync,
    clearLabelCache,
    hasLabel,
    labelFilter
};
