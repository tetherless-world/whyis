/**
 * ID generation utilities
 * @module utilities/id-generator
 */

/**
 * Generate a unique random ID
 * Uses Math.random with base-36 encoding to create short, unique IDs
 * @returns {string} A random ID string (10 characters)
 * @example
 * makeID() // 'k5j2h8g3f1'
 * makeID() // 'p9m4n7b2c6'
 */
export function makeID() {
    // Math.random should be unique because of its seeding algorithm.
    // Convert it to base 36 (numbers + letters), and grab the first 10 characters
    // after the decimal.
    return Math.random().toString(36).substr(2, 10);
}

/**
 * Generate a UUID v4 (if crypto API is available)
 * Falls back to makeID() if crypto API is not available
 * @returns {string} A UUID v4 string or random ID
 * @example
 * generateUUID() // '550e8400-e29b-41d4-a716-446655440000'
 */
export function generateUUID() {
    // Use crypto API if available (browser/node)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    
    // Fallback to custom implementation
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

/**
 * Generate a prefixed ID
 * @param {string} prefix - The prefix to add to the ID
 * @returns {string} A prefixed ID
 * @example
 * makePrefixedID('user') // 'user_k5j2h8g3f1'
 */
export function makePrefixedID(prefix) {
    return `${prefix}_${makeID()}`;
}

/**
 * Generate a timestamp-based ID
 * Combines timestamp with random component for better uniqueness
 * @returns {string} A timestamp-based ID
 * @example
 * makeTimestampID() // '1640000000000_k5j2h8g3f1'
 */
export function makeTimestampID() {
    const timestamp = Date.now();
    const randomPart = makeID();
    return `${timestamp}_${randomPart}`;
}

export default {
    makeID,
    generateUUID,
    makePrefixedID,
    makeTimestampID
};
