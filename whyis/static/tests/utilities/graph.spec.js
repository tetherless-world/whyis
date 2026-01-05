/**
 * Tests for Graph utility
 * @jest-environment jsdom
 */

import axios from 'axios';
import { createGraph, Graph, Resource } from '@/utilities/graph';

// Mock axios
jest.mock('axios');

describe('graph', () => {
    describe('Resource', () => {
        let graph;
        let resource;

        beforeEach(() => {
            graph = createGraph();
            resource = new Resource('http://example.org/resource/1', graph);
        });

        test('should create resource with URI', () => {
            expect(resource.uri).toBe('http://example.org/resource/1');
            expect(resource.graph).toBe(graph);
        });

        test('should initialize empty predicate-object map', () => {
            expect(resource.po).toEqual({});
        });

        describe('values()', () => {
            test('should return empty array for new predicate', () => {
                const vals = resource.values('http://example.org/prop');
                expect(vals).toEqual([]);
            });

            test('should return existing values', () => {
                resource.po['http://example.org/prop'] = ['value1', 'value2'];
                expect(resource.values('http://example.org/prop')).toEqual(['value1', 'value2']);
            });
        });

        describe('has()', () => {
            test('should return false for non-existent predicate', () => {
                expect(resource.has('http://example.org/prop')).toBe(false);
            });

            test('should return false for empty predicate', () => {
                resource.po['http://example.org/prop'] = [];
                expect(resource.has('http://example.org/prop')).toBe(false);
            });

            test('should return true for predicate with values', () => {
                resource.po['http://example.org/prop'] = ['value'];
                expect(resource.has('http://example.org/prop')).toBe(true);
            });
        });

        describe('value()', () => {
            test('should return undefined for non-existent predicate', () => {
                expect(resource.value('http://example.org/prop')).toBeUndefined();
            });

            test('should return first value', () => {
                resource.po['http://example.org/prop'] = ['first', 'second'];
                expect(resource.value('http://example.org/prop')).toBe('first');
            });
        });

        describe('add()', () => {
            test('should add value to predicate', () => {
                resource.add('http://example.org/prop', 'value1');
                expect(resource.values('http://example.org/prop')).toEqual(['value1']);
            });

            test('should add multiple values', () => {
                resource.add('http://example.org/prop', 'value1');
                resource.add('http://example.org/prop', 'value2');
                expect(resource.values('http://example.org/prop')).toEqual(['value1', 'value2']);
            });
        });

        describe('set()', () => {
            test('should set single value', () => {
                resource.set('http://example.org/prop', 'value');
                expect(resource.values('http://example.org/prop')).toEqual(['value']);
            });

            test('should replace existing values', () => {
                resource.add('http://example.org/prop', 'old1');
                resource.add('http://example.org/prop', 'old2');
                resource.set('http://example.org/prop', 'new');
                expect(resource.values('http://example.org/prop')).toEqual(['new']);
            });
        });

        describe('del()', () => {
            test('should delete predicate', () => {
                resource.po['http://example.org/prop'] = ['value'];
                resource.del('http://example.org/prop');
                expect(resource.po['http://example.org/prop']).toBeUndefined();
            });
        });

        describe('get()', () => {
            test('should fetch resource from URI', async () => {
                axios.get.mockResolvedValue({ data: { '@id': resource.uri } });

                await resource.get();

                expect(axios.get).toHaveBeenCalledWith(
                    'http://example.org/resource/1',
                    { headers: { 'Accept': 'application/ld+json;q=1' } }
                );
            });
        });

        describe('toJSON()', () => {
            test('should export resource to JSON-LD', () => {
                resource.add('http://example.org/prop', 'value');
                const json = resource.toJSON();

                expect(json).toEqual({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/prop': ['value']
                });
            });

            test('should handle resource references', () => {
                const other = new Resource('http://example.org/resource/2', graph);
                resource.add('http://example.org/related', other);
                const json = resource.toJSON();

                expect(json['http://example.org/related']).toEqual([
                    { '@id': 'http://example.org/resource/2' }
                ]);
            });

            test('should handle Date objects', () => {
                const date = new Date('2024-01-01T00:00:00Z');
                resource.add('http://example.org/date', date);
                const json = resource.toJSON();

                expect(json['http://example.org/date'][0]).toEqual({
                    '@value': date.toISOString(),
                    '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
                });
            });
        });
    });

    describe('Graph', () => {
        let graph;

        beforeEach(() => {
            graph = createGraph();
        });

        test('should create empty graph', () => {
            expect(graph).toBeInstanceOf(Graph);
            expect(graph).toBeInstanceOf(Array);
            expect(graph.length).toBe(0);
        });

        describe('resource()', () => {
            test('should create new resource', () => {
                const resource = graph.resource('http://example.org/resource/1');

                expect(resource).toBeInstanceOf(Resource);
                expect(resource.uri).toBe('http://example.org/resource/1');
                expect(graph.length).toBe(1);
            });

            test('should return existing resource', () => {
                const r1 = graph.resource('http://example.org/resource/1');
                const r2 = graph.resource('http://example.org/resource/1');

                expect(r1).toBe(r2);
                expect(graph.length).toBe(1);
            });

            test('should add resource to graph array', () => {
                const resource = graph.resource('http://example.org/resource/1');
                expect(graph[0]).toBe(resource);
            });
        });

        describe('ofType()', () => {
            test('should return empty array for new type', () => {
                const resources = graph.ofType('http://example.org/Type');
                expect(resources).toEqual([]);
            });

            test('should return same array on multiple calls', () => {
                const arr1 = graph.ofType('http://example.org/Type');
                const arr2 = graph.ofType('http://example.org/Type');
                expect(arr1).toBe(arr2);
            });
        });

        describe('merge()', () => {
            test('should merge simple resource', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/prop': 'value'
                });

                const resource = graph.resource('http://example.org/resource/1');
                expect(resource.value('http://example.org/prop')).toBe('value');
            });

            test('should handle @type', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    '@type': 'http://example.org/Type'
                });

                const resources = graph.ofType('http://example.org/Type');
                expect(resources.length).toBe(1);
                expect(resources[0].uri).toBe('http://example.org/resource/1');
            });

            test('should handle multiple types', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    '@type': ['http://example.org/Type1', 'http://example.org/Type2']
                });

                expect(graph.ofType('http://example.org/Type1').length).toBe(1);
                expect(graph.ofType('http://example.org/Type2').length).toBe(1);
            });

            test('should handle resource references', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/related': { '@id': 'http://example.org/resource/2' }
                });

                const r1 = graph.resource('http://example.org/resource/1');
                const related = r1.value('http://example.org/related');
                expect(related).toBeInstanceOf(Resource);
                expect(related.uri).toBe('http://example.org/resource/2');
            });

            test('should handle literals with @value', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/prop': { '@value': 'text value' }
                });

                const resource = graph.resource('http://example.org/resource/1');
                expect(resource.value('http://example.org/prop')).toBe('text value');
            });

            test('should convert dateTime values', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/date': {
                        '@value': '2024-01-01T00:00:00Z',
                        '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
                    }
                });

                const resource = graph.resource('http://example.org/resource/1');
                const date = resource.value('http://example.org/date');
                expect(date).toBeInstanceOf(Date);
            });

            test('should handle @graph property', () => {
                graph.merge({
                    '@graph': [
                        { '@id': 'http://example.org/resource/1' },
                        { '@id': 'http://example.org/resource/2' }
                    ]
                });

                expect(graph.length).toBe(2);
            });

            test('should handle array of resources', () => {
                graph.merge([
                    { '@id': 'http://example.org/resource/1' },
                    { '@id': 'http://example.org/resource/2' }
                ]);

                expect(graph.length).toBe(2);
            });

            test('should handle null gracefully', () => {
                expect(() => graph.merge(null)).not.toThrow();
            });

            test('should handle arrays of values', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/prop': ['value1', 'value2']
                });

                const resource = graph.resource('http://example.org/resource/1');
                expect(resource.values('http://example.org/prop')).toEqual(['value1', 'value2']);
            });
        });

        describe('toJSON()', () => {
            test('should export graph to JSON-LD', () => {
                graph.merge({
                    '@id': 'http://example.org/resource/1',
                    'http://example.org/prop': 'value'
                });

                const json = graph.toJSON();

                expect(json).toEqual({
                    '@graph': [
                        {
                            '@id': 'http://example.org/resource/1',
                            'http://example.org/prop': ['value']
                        }
                    ]
                });
            });
        });
    });

    describe('createGraph()', () => {
        test('should create new Graph instance', () => {
            const graph = createGraph();
            expect(graph).toBeInstanceOf(Graph);
        });

        test('should create independent graphs', () => {
            const g1 = createGraph();
            const g2 = createGraph();

            g1.resource('http://example.org/resource/1');

            expect(g1.length).toBe(1);
            expect(g2.length).toBe(0);
        });
    });
});
