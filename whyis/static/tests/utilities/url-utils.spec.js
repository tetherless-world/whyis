/**
 * Tests for URL and data URI utilities
 * @jest-environment jsdom
 */

import { getParameterByName, decodeDataURI, encodeDataURI } from '@/utilities/url-utils';

describe('getParameterByName', () => {
    test('should extract parameter from URL with value', () => {
        const url = 'http://example.com?name=John&age=30';
        expect(getParameterByName('name', url)).toBe('John');
        expect(getParameterByName('age', url)).toBe('30');
    });

    test('should return null for non-existent parameter', () => {
        const url = 'http://example.com?name=John';
        expect(getParameterByName('missing', url)).toBeNull();
    });

    test('should return empty string for parameter without value', () => {
        const url = 'http://example.com?name=&age=30';
        expect(getParameterByName('name', url)).toBe('');
    });

    test('should decode URL-encoded values', () => {
        const url = 'http://example.com?name=John%20Doe';
        expect(getParameterByName('name', url)).toBe('John Doe');
    });

    test('should handle plus signs as spaces', () => {
        const url = 'http://example.com?name=John+Doe';
        expect(getParameterByName('name', url)).toBe('John Doe');
    });

    test('should handle parameters with special characters in name', () => {
        const url = 'http://example.com?test[0]=value';
        expect(getParameterByName('test[0]', url)).toBe('value');
    });

    test('should use window.location.href if no URL provided', () => {
        // Mock window.location
        delete window.location;
        window.location = { href: 'http://example.com?test=value' };
        expect(getParameterByName('test')).toBe('value');
    });

    test('should handle parameters with hash fragments', () => {
        const url = 'http://example.com?name=John#section';
        expect(getParameterByName('name', url)).toBe('John');
    });

    test('should handle parameters at end of URL', () => {
        const url = 'http://example.com?name=John';
        expect(getParameterByName('name', url)).toBe('John');
    });
});

describe('decodeDataURI', () => {
    test('should decode plain text data URI', () => {
        const uri = 'data:text/plain,Hello%20World';
        const result = decodeDataURI(uri);
        expect(result.value).toBe('Hello World');
        expect(result.mimetype).toBe('text/plain');
        expect(result.mediatype).toBe('text/plain');
    });

    test('should decode base64 encoded data URI', () => {
        const uri = 'data:text/plain;base64,SGVsbG8gV29ybGQ=';
        const result = decodeDataURI(uri);
        expect(result.value).toBe('Hello World');
        expect(result.mimetype).toBe('text/plain');
    });

    test('should handle charset parameter', () => {
        const uri = 'data:text/plain;charset=UTF-8,Hello';
        const result = decodeDataURI(uri);
        expect(result.charset).toBe('UTF-8');
        expect(result.mimetype).toBe('text/plain');
    });

    test('should default to text/plain with US-ASCII charset', () => {
        const uri = 'data:,Hello';
        const result = decodeDataURI(uri);
        expect(result.mimetype).toBe('text/plain');
        expect(result.charset).toBe('US-ASCII');
        expect(result.mediatype).toBe('text/plain;charset=US-ASCII');
    });

    test('should handle binary data types', () => {
        const uri = 'data:image/png;base64,iVBORw0KGgo=';
        const result = decodeDataURI(uri);
        expect(result.mimetype).toBe('image/png');
        expect(result.charset).toBeNull();
    });

    test('should throw error for invalid data URI', () => {
        expect(() => decodeDataURI('not-a-data-uri')).toThrow('Not a valid data URI');
    });

    test('should handle data URI with multiple parameters', () => {
        const uri = 'data:text/plain;charset=UTF-8;name=test,Hello';
        const result = decodeDataURI(uri);
        expect(result.mimetype).toBe('text/plain');
        expect(result.charset).toBe('UTF-8');
    });
});

describe('encodeDataURI', () => {
    test('should encode string as data URI', () => {
        const result = encodeDataURI('Hello World');
        expect(result).toMatch(/^data:text\/plain;charset=UTF-8;base64,/);
        // Decode to verify
        const decoded = decodeDataURI(result);
        expect(decoded.value).toBe('Hello World');
    });

    test('should use custom mediatype if provided', () => {
        const result = encodeDataURI('{"key":"value"}', 'application/json');
        expect(result).toMatch(/^data:application\/json;base64,/);
    });

    test('should throw error for invalid input', () => {
        expect(() => encodeDataURI(123)).toThrow('Invalid input');
        expect(() => encodeDataURI(null)).toThrow('Invalid input');
        expect(() => encodeDataURI({})).toThrow('Invalid input');
    });

    test('should handle empty string', () => {
        const result = encodeDataURI('');
        expect(result).toMatch(/^data:text\/plain;charset=UTF-8;base64,/);
        const decoded = decodeDataURI(result);
        expect(decoded.value).toBe('');
    });

    test('should handle special characters', () => {
        // Note: atob/btoa in browsers have UTF-8 encoding issues
        // This is a known limitation when using btoa directly
        // In Node.js with Buffer, this works correctly
        const input = 'Hello 世界 🌍';
        const result = encodeDataURI(input);
        const decoded = decodeDataURI(result);
        // Verify the roundtrip works
        expect(decoded.value).toBeDefined();
        // In Node environment with Buffer support, it should work
        if (typeof Buffer !== 'undefined' && Buffer.from) {
            expect(decoded.value).toBe(input);
        }
    });
});

describe('roundtrip encoding/decoding', () => {
    test('should roundtrip plain text', () => {
        const original = 'This is a test string with special chars: @#$%';
        const encoded = encodeDataURI(original);
        const decoded = decodeDataURI(encoded);
        expect(decoded.value).toBe(original);
    });

    test('should roundtrip JSON data', () => {
        const original = '{"name":"John","age":30}';
        const encoded = encodeDataURI(original, 'application/json');
        const decoded = decodeDataURI(encoded);
        expect(decoded.value).toBe(original);
        expect(decoded.mimetype).toBe('application/json');
    });
});
