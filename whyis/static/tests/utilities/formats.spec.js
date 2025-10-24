/**
 * Tests for formats utility
 * @jest-environment jsdom
 */

import {
    getFormatByExtension,
    getFormatByMimetype,
    getExtension,
    getFormatFromFilename,
    isFormatSupported,
    getAllFormats,
    getAllExtensions
} from '@/utilities/formats';

describe('formats utility', () => {
    describe('getFormatByExtension', () => {
        test('should return format for valid RDF extension', () => {
            const format = getFormatByExtension('ttl');
            expect(format).toBeDefined();
            expect(format.mimetype).toBe('text/turtle');
            expect(format.name).toBe('Turtle');
        });

        test('should return format for JSON-LD', () => {
            const format = getFormatByExtension('jsonld');
            expect(format).toBeDefined();
            expect(format.mimetype).toBe('application/ld+json');
            expect(format.name).toBe('JSON-LD');
        });

        test('should return format for RDF/XML', () => {
            const format = getFormatByExtension('rdf');
            expect(format).toBeDefined();
            expect(format.mimetype).toBe('application/rdf+xml');
        });

        test('should return undefined for unsupported extension', () => {
            const format = getFormatByExtension('xyz');
            expect(format).toBeUndefined();
        });

        test('should handle all RDF formats', () => {
            const extensions = ['rdf', 'json', 'jsonld', 'ttl', 'trig', 'nq', 'nquads', 'nt', 'ntriples'];
            extensions.forEach(ext => {
                const format = getFormatByExtension(ext);
                expect(format).toBeDefined();
                expect(format.mimetype).toBeDefined();
            });
        });
    });

    describe('getFormatByMimetype', () => {
        test('should return format for Turtle mimetype', () => {
            const format = getFormatByMimetype('text/turtle');
            expect(format).toBeDefined();
            expect(format.name).toBe('Turtle');
            expect(format.extensions).toContain('ttl');
        });

        test('should return format for JSON-LD mimetype', () => {
            const format = getFormatByMimetype('application/ld+json');
            expect(format).toBeDefined();
            expect(format.name).toBe('JSON-LD');
        });

        test('should return undefined for unknown mimetype', () => {
            const format = getFormatByMimetype('application/unknown');
            expect(format).toBeUndefined();
        });

        test('should handle all RDF mimetypes', () => {
            const mimetypes = [
                'application/rdf+xml',
                'application/ld+json',
                'text/turtle',
                'application/trig',
                'application/n-quads',
                'application/n-triples'
            ];
            mimetypes.forEach(mimetype => {
                const format = getFormatByMimetype(mimetype);
                expect(format).toBeDefined();
                expect(format.mimetype).toBe(mimetype);
            });
        });
    });

    describe('getExtension', () => {
        test('should extract extension from simple filename', () => {
            expect(getExtension('data.ttl')).toBe('ttl');
            expect(getExtension('file.json')).toBe('json');
            expect(getExtension('ontology.rdf')).toBe('rdf');
        });

        test('should handle filenames with multiple dots', () => {
            expect(getExtension('my.data.file.ttl')).toBe('ttl');
            expect(getExtension('archive.tar.gz')).toBe('gz');
        });

        test('should handle filenames without extension', () => {
            expect(getExtension('README')).toBe('');
            expect(getExtension('file')).toBe('');
        });

        test('should handle empty or null input', () => {
            expect(getExtension('')).toBe('');
            expect(getExtension(null)).toBe('');
            expect(getExtension(undefined)).toBe('');
        });

        test('should be case-insensitive', () => {
            expect(getExtension('file.TTL')).toBe('ttl');
            expect(getExtension('DATA.RDF')).toBe('rdf');
        });
    });

    describe('getFormatFromFilename', () => {
        test('should get format from complete filename', () => {
            const format = getFormatFromFilename('ontology.ttl');
            expect(format).toBeDefined();
            expect(format.mimetype).toBe('text/turtle');
        });

        test('should work with path', () => {
            const format = getFormatFromFilename('/path/to/data.jsonld');
            expect(format).toBeDefined();
            expect(format.mimetype).toBe('application/ld+json');
        });

        test('should return undefined for unsupported format', () => {
            const format = getFormatFromFilename('document.pdf');
            expect(format).toBeUndefined();
        });

        test('should handle filename without extension', () => {
            const format = getFormatFromFilename('README');
            expect(format).toBeUndefined();
        });
    });

    describe('isFormatSupported', () => {
        test('should return true for supported extensions', () => {
            expect(isFormatSupported('ttl')).toBe(true);
            expect(isFormatSupported('json')).toBe(true);
            expect(isFormatSupported('rdf')).toBe(true);
        });

        test('should return false for unsupported extensions', () => {
            expect(isFormatSupported('pdf')).toBe(false);
            expect(isFormatSupported('doc')).toBe(false);
            expect(isFormatSupported('xyz')).toBe(false);
        });

        test('should handle undefined or empty input', () => {
            expect(isFormatSupported(undefined)).toBe(false);
            expect(isFormatSupported('')).toBe(false);
        });
    });

    describe('getAllFormats', () => {
        test('should return array of all formats', () => {
            const formats = getAllFormats();
            expect(Array.isArray(formats)).toBe(true);
            expect(formats.length).toBeGreaterThan(0);
        });

        test('should include all major RDF formats', () => {
            const formats = getAllFormats();
            const mimetypes = formats.map(f => f.mimetype);
            
            expect(mimetypes).toContain('text/turtle');
            expect(mimetypes).toContain('application/ld+json');
            expect(mimetypes).toContain('application/rdf+xml');
            expect(mimetypes).toContain('application/trig');
        });

        test('should return a copy, not the original array', () => {
            const formats1 = getAllFormats();
            const formats2 = getAllFormats();
            
            expect(formats1).not.toBe(formats2);
            expect(formats1).toEqual(formats2);
        });
    });

    describe('getAllExtensions', () => {
        test('should return array of all extensions', () => {
            const extensions = getAllExtensions();
            expect(Array.isArray(extensions)).toBe(true);
            expect(extensions.length).toBeGreaterThan(0);
        });

        test('should include common RDF extensions', () => {
            const extensions = getAllExtensions();
            
            expect(extensions).toContain('ttl');
            expect(extensions).toContain('json');
            expect(extensions).toContain('jsonld');
            expect(extensions).toContain('rdf');
        });

        test('should include all defined extensions', () => {
            const extensions = getAllExtensions();
            
            // Should include at least these extensions
            const expectedExtensions = ['rdf', 'json', 'jsonld', 'ttl', 'trig', 'nq', 'nt'];
            expectedExtensions.forEach(ext => {
                expect(extensions).toContain(ext);
            });
        });
    });

    describe('format structure', () => {
        test('each format should have required properties', () => {
            const formats = getAllFormats();
            
            formats.forEach(format => {
                expect(format).toHaveProperty('mimetype');
                expect(format).toHaveProperty('name');
                expect(format).toHaveProperty('extensions');
                expect(Array.isArray(format.extensions)).toBe(true);
                expect(format.extensions.length).toBeGreaterThan(0);
            });
        });

        test('format names should be descriptive', () => {
            const format = getFormatByExtension('ttl');
            expect(format.name).toBe('Turtle');
            
            const jsonldFormat = getFormatByExtension('jsonld');
            expect(jsonldFormat.name).toBe('JSON-LD');
        });
    });
});
