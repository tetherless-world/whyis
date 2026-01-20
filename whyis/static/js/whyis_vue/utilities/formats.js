/**
 * RDF and semantic data format definitions
 * @module utilities/formats
 */

/**
 * Format definition for RDF and semantic data types
 * @typedef {Object} Format
 * @property {string} mimetype - The MIME type
 * @property {string} name - Human-readable format name
 * @property {string[]} extensions - File extensions associated with this format
 */

/**
 * List of supported RDF and semantic data formats
 * @type {Format[]}
 */
const formats = [
    { mimetype: "application/rdf+xml", name: "RDF/XML", extensions: ["rdf"] },
    { mimetype: "application/ld+json", name: 'JSON-LD', extensions: ["json", 'jsonld'] },
    { mimetype: "text/turtle", name: "Turtle", extensions: ['ttl'] },
    { mimetype: "application/trig", name: "TRiG", extensions: ['trig'] },
    { mimetype: "application/n-quads", name: "n-Quads", extensions: ['nq', 'nquads'] },
    { mimetype: "application/n-triples", name: "N-Triples", extensions: ['nt', 'ntriples'] },
];

/**
 * Lookup table mapping file extensions to format objects
 * @type {Object.<string, Format>}
 */
const lookup = {};

// Build the lookup table for primary formats
formats.forEach(format => {
    format.extensions.forEach(extension => {
        lookup[extension] = format;
    });
});

// Add additional formats (these override previous entries for conflicting extensions)
[
    { mimetype: "text/html", name: "HTML+RDFa", extensions: ['html', 'htm'] },
    { mimetype: "text/markdown", name: "Semantic Markdown", extensions: ['md', 'markdown'] },
].forEach(format => {
    format.extensions.forEach(extension => {
        lookup[extension] = format;
    });
});

/**
 * Get format information by file extension
 * @param {string} extension - The file extension (without dot)
 * @returns {Format|undefined} The format object or undefined if not found
 * @example
 * getFormatByExtension('ttl') // { mimetype: "text/turtle", name: "Turtle", extensions: ['ttl'] }
 */
export function getFormatByExtension(extension) {
    return lookup[extension];
}

/**
 * Get format information by MIME type
 * @param {string} mimetype - The MIME type to search for
 * @returns {Format|undefined} The format object or undefined if not found
 * @example
 * getFormatByMimetype('text/turtle') // { mimetype: "text/turtle", name: "Turtle", extensions: ['ttl'] }
 */
export function getFormatByMimetype(mimetype) {
    return formats.find(f => f.mimetype === mimetype);
}

/**
 * Extract file extension from filename
 * @param {string} filename - The filename to extract extension from
 * @returns {string} The file extension (without dot), or empty string if none
 * @example
 * getExtension('data.ttl') // 'ttl'
 * getExtension('file.json') // 'json'
 */
export function getExtension(filename) {
    if (!filename) return '';
    const parts = filename.split('.');
    if (parts.length < 2) return '';
    return parts[parts.length - 1].toLowerCase();
}

/**
 * Get format information from a filename
 * @param {string} filename - The filename to analyze
 * @returns {Format|undefined} The format object or undefined if not recognized
 * @example
 * getFormatFromFilename('data.ttl') // { mimetype: "text/turtle", name: "Turtle", extensions: ['ttl'] }
 */
export function getFormatFromFilename(filename) {
    const extension = getExtension(filename);
    return getFormatByExtension(extension);
}

/**
 * Check if a file extension is supported
 * @param {string} extension - The file extension to check
 * @returns {boolean} True if the extension is recognized
 * @example
 * isFormatSupported('ttl') // true
 * isFormatSupported('xyz') // false
 */
export function isFormatSupported(extension) {
    return lookup[extension] !== undefined;
}

/**
 * Get all supported formats
 * @returns {Format[]} Array of all format definitions
 */
export function getAllFormats() {
    return [...formats];
}

/**
 * Get all supported extensions
 * @returns {string[]} Array of all supported file extensions
 */
export function getAllExtensions() {
    return Object.keys(lookup);
}

export default {
    formats,
    lookup,
    getFormatByExtension,
    getFormatByMimetype,
    getExtension,
    getFormatFromFilename,
    isFormatSupported,
    getAllFormats,
    getAllExtensions
};
