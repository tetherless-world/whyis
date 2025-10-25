/**
 * Tests for URI resolver utility
 * @jest-environment jsdom
 */

import { resolveURI, compactURI, isFullURI } from '@/utilities/uri-resolver';

describe('uri-resolver', () => {
    describe('resolveURI', () => {
        test('should return URI as-is if no context', () => {
            expect(resolveURI('http://example.org/test')).toBe('http://example.org/test');
        });

        test('should expand prefix with simple mapping', () => {
            const context = {
                'dc': 'http://purl.org/dc/terms/'
            };
            expect(resolveURI('dc:title', context)).toBe('http://purl.org/dc/terms/title');
        });

        test('should handle multiple prefixes', () => {
            const context = {
                'dc': 'http://purl.org/dc/terms/',
                'foaf': 'http://xmlns.com/foaf/0.1/'
            };
            expect(resolveURI('dc:title', context)).toBe('http://purl.org/dc/terms/title');
            expect(resolveURI('foaf:name', context)).toBe('http://xmlns.com/foaf/0.1/name');
        });

        test('should handle @id in prefix definition', () => {
            const context = {
                'dc': { '@id': 'http://purl.org/dc/terms/' }
            };
            expect(resolveURI('dc:title', context)).toBe('http://purl.org/dc/terms/title');
        });

        test('should apply @vocab for terms without prefix', () => {
            const context = {
                '@vocab': 'http://example.org/vocab/'
            };
            expect(resolveURI('label', context)).toBe('http://example.org/vocab/label');
        });

        test('should not apply @vocab to full URIs', () => {
            const context = {
                '@vocab': 'http://example.org/vocab/'
            };
            expect(resolveURI('http://other.org/prop', context)).toBe('http://other.org/prop');
        });

        test('should resolve direct term mappings', () => {
            const context = {
                'name': 'http://schema.org/name'
            };
            expect(resolveURI('name', context)).toBe('http://schema.org/name');
        });

        test('should recursively resolve mapped terms', () => {
            const context = {
                'title': 'dc:title',
                'dc': 'http://purl.org/dc/terms/'
            };
            expect(resolveURI('title', context)).toBe('http://purl.org/dc/terms/title');
        });

        test('should handle empty context', () => {
            expect(resolveURI('test:prop', {})).toBe('test:prop');
        });

        test('should handle undefined context', () => {
            expect(resolveURI('test:prop')).toBe('test:prop');
        });

        test('should preserve fragments in URIs', () => {
            const context = {
                'ex': 'http://example.org/'
            };
            expect(resolveURI('ex:term#fragment', context)).toBe('http://example.org/term#fragment');
        });
    });

    describe('compactURI', () => {
        test('should return URI as-is if no matching prefix', () => {
            const context = {};
            expect(compactURI('http://example.org/test', context)).toBe('http://example.org/test');
        });

        test('should compact URI with matching prefix', () => {
            const context = {
                'dc': 'http://purl.org/dc/terms/'
            };
            expect(compactURI('http://purl.org/dc/terms/title', context)).toBe('dc:title');
        });

        test('should use @vocab for compaction', () => {
            const context = {
                '@vocab': 'http://example.org/vocab/'
            };
            expect(compactURI('http://example.org/vocab/label', context)).toBe('label');
        });

        test('should prefer prefixes over @vocab', () => {
            const context = {
                'ex': 'http://example.org/',
                '@vocab': 'http://example.org/'
            };
            const result = compactURI('http://example.org/test', context);
            expect(result).toBe('ex:test');
        });

        test('should handle @id in prefix definitions', () => {
            const context = {
                'dc': { '@id': 'http://purl.org/dc/terms/' }
            };
            expect(compactURI('http://purl.org/dc/terms/title', context)).toBe('dc:title');
        });

        test('should skip special keys in context', () => {
            const context = {
                '@id': 'should-be-ignored',
                '@graph': 'should-be-ignored',
                'dc': 'http://purl.org/dc/terms/'
            };
            expect(compactURI('http://purl.org/dc/terms/title', context)).toBe('dc:title');
        });

        test('should handle empty context', () => {
            expect(compactURI('http://example.org/test', {})).toBe('http://example.org/test');
        });
    });

    describe('isFullURI', () => {
        test('should return true for HTTP URIs', () => {
            expect(isFullURI('http://example.org/test')).toBe(true);
            expect(isFullURI('https://example.org/test')).toBe(true);
        });

        test('should return true for other protocols', () => {
            expect(isFullURI('ftp://example.org/file')).toBe(true);
            expect(isFullURI('file:///path/to/file')).toBe(true);
            expect(isFullURI('urn:isbn:0451450523')).toBe(true);
        });

        test('should return false for compact IRIs', () => {
            expect(isFullURI('dc:title')).toBe(false);
            expect(isFullURI('foaf:name')).toBe(false);
        });

        test('should return false for simple terms', () => {
            expect(isFullURI('label')).toBe(false);
            expect(isFullURI('name')).toBe(false);
        });

        test('should handle edge cases', () => {
            expect(isFullURI('')).toBe(false);
            expect(isFullURI(':')).toBe(false);
            expect(isFullURI('123:test')).toBe(false); // Doesn't start with letter
        });
    });

    describe('integration tests', () => {
        test('should roundtrip resolve and compact', () => {
            const context = {
                'dc': 'http://purl.org/dc/terms/',
                'foaf': 'http://xmlns.com/foaf/0.1/'
            };

            const compactUri = 'dc:title';
            const fullUri = resolveURI(compactUri, context);
            const backToCompact = compactURI(fullUri, context);

            expect(fullUri).toBe('http://purl.org/dc/terms/title');
            expect(backToCompact).toBe(compactUri);
        });

        test('should handle complex nested context', () => {
            const context = {
                'schema': 'http://schema.org/',
                'name': 'schema:name',
                '@vocab': 'http://example.org/'
            };

            expect(resolveURI('name', context)).toBe('http://schema.org/name');
            expect(resolveURI('label', context)).toBe('http://example.org/label');
        });
    });
});
