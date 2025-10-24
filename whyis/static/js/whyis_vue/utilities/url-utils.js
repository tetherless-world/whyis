/**
 * URL and data URI utilities
 * @module utilities/url-utils
 */

/**
 * Get a parameter value from a URL query string
 * @param {string} name - The parameter name to retrieve
 * @param {string} [url] - The URL to parse (defaults to current window location)
 * @returns {string|null} The parameter value or null if not found
 * @example
 * // URL: http://example.com?foo=bar&baz=qux
 * getParameterByName('foo') // returns 'bar'
 * getParameterByName('missing') // returns null
 */
export function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

/**
 * Decode a data URI and return its contents and metadata
 * @param {string} uri - The data URI to decode
 * @returns {Object} An object containing value, mimetype, mediatype, and charset
 * @throws {Error} If the URI is not a valid data URI
 * @example
 * const result = decodeDataURI('data:text/plain;base64,SGVsbG8gV29ybGQ=');
 * // result.value = 'Hello World'
 * // result.mimetype = 'text/plain'
 */
export function decodeDataURI(uri) {
    // dataurl    := "data:" [ mediatype ] [ ";base64" ] "," data
    // mediatype  := [ type "/" subtype ] *( ";" parameter )
    // data       := *urlchar
    // parameter  := attribute "=" value

    const m = /^data:([^;,]+)?((?:;(?:[^;,]+))*?)(;base64)?,(.*)/.exec(uri);
    if (!m) {
        throw new Error('Not a valid data URI: "' + uri.slice(0, 20) + '"');
    }

    let media = '';
    const b64 = m[3];
    const body = m[4];
    let charset = null;
    let mimetype = null;

    // If <mediatype> is omitted, it defaults to text/plain;charset=US-ASCII.
    // As a shorthand, "text/plain" can be omitted but the charset parameter supplied.
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
    // so we will return null. For example, charset doesn't make sense for
    // binary types like image/png
    if (!charset && m[2]) {
        const cm = /;charset=([^;,]+)/.exec(m[2]);
        if (cm) {
            charset = cm[1];
        }
    }

    let value;
    if (b64) {
        // Use Buffer.from in Node.js for proper UTF-8 support
        if (typeof Buffer !== 'undefined' && Buffer.from) {
            value = Buffer.from(body, 'base64').toString('utf8');
        } else {
            // Browser fallback using atob
            value = atob(body);
        }
    } else {
        value = decodeURIComponent(body);
    }

    return {
        value,
        mimetype,
        mediatype: media,
        charset
    };
}

/**
 * Encode data as a data URI
 * @param {string|Buffer} input - The data to encode
 * @param {string} [mediatype] - The media type (defaults based on input type)
 * @returns {string} The data URI
 * @throws {Error} If input is not a string or Buffer
 */
export function encodeDataURI(input, mediatype) {
    if (typeof Buffer !== 'undefined' && Buffer.isBuffer && Buffer.isBuffer(input)) {
        // Handle Buffer input
        mediatype = mediatype || 'application/octet-stream';
        const base64 = input.toString('base64');
        return 'data:' + mediatype + ';base64,' + base64;
    } else if (typeof input === 'string') {
        mediatype = mediatype || 'text/plain;charset=UTF-8';
        
        // Use Buffer if available (Node.js)
        if (typeof Buffer !== 'undefined' && Buffer.from) {
            const buf = Buffer.from(input, 'utf8');
            const base64 = buf.toString('base64');
            return 'data:' + mediatype + ';base64,' + base64;
        } else {
            // Browser fallback using btoa
            // For Unicode support, encode as UTF-8 first
            const base64 = btoa(unescape(encodeURIComponent(input)));
            return 'data:' + mediatype + ';base64,' + base64;
        }
    } else {
        throw new Error('Invalid input, expected Buffer or string');
    }
}
