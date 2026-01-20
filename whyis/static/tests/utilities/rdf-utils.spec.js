/**
 * Tests for RDF utilities
 * @jest-environment jsdom
 */

import { listify, getSummary, getSummaryProperties, SUMMARY_PROPERTIES } from '@/utilities/rdf-utils';

describe('rdf-utils', () => {
    describe('listify', () => {
        test('should return arrays unchanged', () => {
            const arr = [1, 2, 3];
            expect(listify(arr)).toBe(arr);
        });

        test('should wrap non-arrays in array', () => {
            expect(listify('string')).toEqual(['string']);
            expect(listify(42)).toEqual([42]);
            expect(listify(null)).toEqual([null]);
            expect(listify(undefined)).toEqual([undefined]);
        });

        test('should handle objects without forEach', () => {
            const obj = { key: 'value' };
            expect(listify(obj)).toEqual([obj]);
        });

        test('should handle empty arrays', () => {
            const arr = [];
            expect(listify(arr)).toBe(arr);
        });

        test('should preserve array-like objects with forEach', () => {
            const arrayLike = {
                0: 'a',
                1: 'b',
                length: 2,
                forEach: Array.prototype.forEach
            };
            expect(listify(arrayLike)).toBe(arrayLike);
        });
    });

    describe('getSummary', () => {
        test('should extract description from entity', () => {
            const entity = {
                'http://purl.org/dc/terms/description': [
                    { '@value': 'This is a description' }
                ]
            };
            expect(getSummary(entity)).toBe('This is a description');
        });

        test('should extract definition from entity', () => {
            const entity = {
                'http://www.w3.org/2004/02/skos/core#definition': [
                    { '@value': 'This is a definition' }
                ]
            };
            expect(getSummary(entity)).toBe('This is a definition');
        });

        test('should handle plain string values', () => {
            const entity = {
                'http://purl.org/dc/terms/description': ['Plain string']
            };
            expect(getSummary(entity)).toBe('Plain string');
        });

        test('should prefer definition over description', () => {
            const entity = {
                'http://www.w3.org/2004/02/skos/core#definition': [
                    { '@value': 'Definition' }
                ],
                'http://purl.org/dc/terms/description': [
                    { '@value': 'Description' }
                ]
            };
            expect(getSummary(entity)).toBe('Definition');
        });

        test('should return first value if multiple exist', () => {
            const entity = {
                'http://purl.org/dc/terms/description': [
                    { '@value': 'First description' },
                    { '@value': 'Second description' }
                ]
            };
            expect(getSummary(entity)).toBe('First description');
        });

        test('should check properties in order of preference', () => {
            const entity = {
                'http://www.w3.org/2000/01/rdf-schema#comment': [
                    { '@value': 'Comment' }
                ],
                'http://purl.org/dc/terms/abstract': [
                    { '@value': 'Abstract' }
                ]
            };
            // Abstract should be preferred over comment
            expect(getSummary(entity)).toBe('Abstract');
        });

        test('should return undefined for entity without summary properties', () => {
            const entity = {
                'http://www.w3.org/2000/01/rdf-schema#label': 'Label only'
            };
            expect(getSummary(entity)).toBeUndefined();
        });

        test('should return undefined for null entity', () => {
            expect(getSummary(null)).toBeUndefined();
        });

        test('should return undefined for undefined entity', () => {
            expect(getSummary(undefined)).toBeUndefined();
        });

        test('should handle empty entity object', () => {
            expect(getSummary({})).toBeUndefined();
        });

        test('should handle all summary property types', () => {
            const properties = [
                'http://www.w3.org/2004/02/skos/core#definition',
                'http://purl.org/dc/terms/abstract',
                'http://purl.org/dc/terms/description',
                'http://purl.org/dc/terms/summary',
                'http://www.w3.org/2000/01/rdf-schema#comment',
                'http://purl.obolibrary.org/obo/IAO_0000115',
                'http://www.w3.org/ns/prov#value',
                'http://semanticscience.org/resource/hasValue'
            ];

            properties.forEach(prop => {
                const entity = {
                    [prop]: [{ '@value': `Summary for ${prop}` }]
                };
                expect(getSummary(entity)).toBe(`Summary for ${prop}`);
            });
        });
    });

    describe('getSummaryProperties', () => {
        test('should return array of property URIs', () => {
            const props = getSummaryProperties();
            expect(Array.isArray(props)).toBe(true);
            expect(props.length).toBeGreaterThan(0);
        });

        test('should return a copy, not the original array', () => {
            const props1 = getSummaryProperties();
            const props2 = getSummaryProperties();
            expect(props1).not.toBe(props2);
            expect(props1).toEqual(props2);
        });

        test('should match SUMMARY_PROPERTIES constant', () => {
            const props = getSummaryProperties();
            expect(props).toEqual(SUMMARY_PROPERTIES);
        });
    });

    describe('SUMMARY_PROPERTIES constant', () => {
        test('should be an array', () => {
            expect(Array.isArray(SUMMARY_PROPERTIES)).toBe(true);
        });

        test('should contain expected properties', () => {
            expect(SUMMARY_PROPERTIES).toContain('http://purl.org/dc/terms/description');
            expect(SUMMARY_PROPERTIES).toContain('http://www.w3.org/2004/02/skos/core#definition');
            expect(SUMMARY_PROPERTIES).toContain('http://www.w3.org/2000/01/rdf-schema#comment');
        });

        test('should have definition as highest priority', () => {
            expect(SUMMARY_PROPERTIES[0]).toBe('http://www.w3.org/2004/02/skos/core#definition');
        });
    });
});
