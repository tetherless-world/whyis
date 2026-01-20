/**
 * URI resolution utilities for JSON-LD contexts
 * @module utilities/uri-resolver
 */

/**
 * Resolve a URI using a JSON-LD context
 * Handles prefix expansion and vocabulary resolution
 * @param {string} uri - The URI or compact IRI to resolve
 * @param {Object} [context={}] - The JSON-LD context
 * @returns {string} The resolved full URI
 * @example
 * const context = {
 *   'dc': 'http://purl.org/dc/terms/',
 *   '@vocab': 'http://example.org/vocab/'
 * };
 * resolveURI('dc:title', context) // 'http://purl.org/dc/terms/title'
 * resolveURI('label', context) // 'http://example.org/vocab/label'
 */
export function resolveURI(uri, context = {}) {
    // Check if URI is mapped directly in context
    if (context[uri]) {
        // Recursively resolve in case the mapping is also a prefix
        return resolveURI(context[uri], context);
    }
    
    // Check if URI contains a prefix (has colon)
    const colonIndex = uri.indexOf(':');
    if (colonIndex !== -1) {
        const prefix = uri.slice(0, colonIndex);
        const local = uri.slice(colonIndex + 1);
        
        // Check if prefix is defined in context
        if (context[prefix]) {
            let c = context[prefix];
            // Handle @id in context definition
            if (c && c['@id']) {
                c = c['@id'];
            }
            // Recursively resolve the expanded URI
            return resolveURI(c + local, context);
        }
    }
    
    // Check for @vocab
    if (context['@vocab']) {
        // Only apply @vocab if URI doesn't look like a full URI (no colon or starts with http)
        if (colonIndex === -1) {
            return context['@vocab'] + uri;
        }
    }
    
    // Return URI as-is if no resolution possible
    return uri;
}

/**
 * Compact a full URI using a JSON-LD context
 * This is the reverse of resolveURI
 * @param {string} fullUri - The full URI to compact
 * @param {Object} [context={}] - The JSON-LD context
 * @returns {string} The compacted URI (prefix:local or term)
 * @example
 * const context = {
 *   'dc': 'http://purl.org/dc/terms/'
 * };
 * compactURI('http://purl.org/dc/terms/title', context) // 'dc:title'
 */
export function compactURI(fullUri, context = {}) {
    // Try to find a matching prefix
    for (const [key, value] of Object.entries(context)) {
        if (key === '@vocab' || key === '@id' || key === '@graph') continue;
        
        let baseUri = value;
        if (baseUri && baseUri['@id']) {
            baseUri = baseUri['@id'];
        }
        
        if (typeof baseUri === 'string' && fullUri.startsWith(baseUri)) {
            const local = fullUri.slice(baseUri.length);
            return `${key}:${local}`;
        }
    }
    
    // Try @vocab
    if (context['@vocab'] && fullUri.startsWith(context['@vocab'])) {
        return fullUri.slice(context['@vocab'].length);
    }
    
    // Return full URI if no compaction possible
    return fullUri;
}

/**
 * Check if a string is a full URI (contains protocol)
 * @param {string} str - The string to check
 * @returns {boolean} True if it's a full URI
 * @example
 * isFullURI('http://example.org/test') // true
 * isFullURI('dc:title') // false
 */
export function isFullURI(str) {
    // Check for protocol pattern (scheme://... or scheme:... but not prefix:localpart)
    // Must have // after colon OR be a known scheme like urn:
    return /^[a-z][a-z0-9+.-]*:\/\//i.test(str) || /^urn:/i.test(str);
}

export default {
    resolveURI,
    compactURI,
    isFullURI
};
