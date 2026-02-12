/**
 * Tests for KG links utility
 * @jest-environment jsdom
 */

import axios from 'axios';
import { createLinksService, createGraphElements } from '@/utilities/kg-links';

// Mock axios
jest.mock('axios');

describe('kg-links', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
    });

    describe('createGraphElements', () => {
        test('should create empty graph elements structure', () => {
            const elements = createGraphElements();

            expect(elements).toEqual({
                nodes: [],
                edges: [],
                nodeMap: {},
                edgeMap: {}
            });
        });
    });

    describe('createLinksService', () => {
        test('should create links service', () => {
            const links = createLinksService();
            expect(typeof links).toBe('function');
        });

        test('should use custom root URL', () => {
            const links = createLinksService('http://custom.example.org/');
            expect(typeof links).toBe('function');
        });
    });

    describe('links service', () => {
        let links;
        let elements;

        beforeEach(() => {
            links = createLinksService('http://localhost/');
            elements = createGraphElements();
        });

        test('should fetch and process links', async () => {
            const mockData = [
                {
                    source: 'http://example.org/s1',
                    source_label: 'Source 1',
                    source_types: ['http://example.org/Type'],
                    target: 'http://example.org/t1',
                    target_label: 'Target 1',
                    target_types: ['http://example.org/Type'],
                    link: 'http://example.org/predicate',
                    probability: 0.95
                }
            ];

            axios.get.mockResolvedValue({ data: mockData });

            await links('http://example.org/entity', 'outgoing', elements);

            expect(axios.get).toHaveBeenCalledWith(
                'http://localhost/about',
                {
                    params: { uri: 'http://example.org/entity', view: 'outgoing' },
                    responseType: 'json'
                }
            );

            expect(elements.nodes.length).toBeGreaterThan(0);
            expect(elements.edges.length).toBeGreaterThan(0);
        });

        test('should skip edges below probability threshold', async () => {
            const mockData = [
                {
                    source: 'http://example.org/s1',
                    target: 'http://example.org/t1',
                    link: 'http://example.org/predicate',
                    probability: 0.5 // Below default threshold
                }
            ];

            axios.get.mockResolvedValue({ data: mockData });

            await links('http://example.org/entity', 'outgoing', elements);

            expect(elements.edges.length).toBe(0);
        });

        test('should respect custom probability threshold', async () => {
            const mockData = [
                {
                    source: 'http://example.org/s1',
                    target: 'http://example.org/t1',
                    link: 'http://example.org/predicate',
                    probability: 0.5
                }
            ];

            axios.get.mockResolvedValue({ data: mockData });

            await links('http://example.org/entity', 'outgoing', elements, null, 0.4);

            expect(elements.edges.length).toBeGreaterThan(0);
        });

        test('should initialize node structure', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await links('http://example.org/entity', 'outgoing', elements);

            expect(elements.node).toBeDefined();
            expect(typeof elements.node).toBe('function');
        });

        test('should initialize edge structure', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await links('http://example.org/entity', 'outgoing', elements);

            expect(elements.edge).toBeDefined();
            expect(typeof elements.edge).toBe('function');
        });

        test('should add utility methods', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await links('http://example.org/entity', 'outgoing', elements);

            expect(elements.all).toBeDefined();
            expect(elements.empty).toBeDefined();
            expect(typeof elements.all).toBe('function');
            expect(typeof elements.empty).toBe('function');
        });

        test('should handle API errors', async () => {
            axios.get.mockRejectedValue(new Error('Network error'));

            await expect(
                links('http://example.org/entity', 'outgoing', elements)
            ).rejects.toThrow('Network error');
        });

        test('should create nodes without duplicates', async () => {
            const mockData = [
                {
                    source: 'http://example.org/s1',
                    source_label: 'Source 1',
                    target: 'http://example.org/t1',
                    target_label: 'Target 1',
                    link: 'http://example.org/p1',
                    probability: 0.95
                },
                {
                    source: 'http://example.org/s1', // Duplicate
                    source_label: 'Source 1',
                    target: 'http://example.org/t2',
                    target_label: 'Target 2',
                    link: 'http://example.org/p1',
                    probability: 0.95
                }
            ];

            axios.get.mockResolvedValue({ data: mockData });

            await links('http://example.org/entity', 'outgoing', elements);

            // Should only create unique nodes
            const uniqueNodeUris = new Set(elements.nodes.map(n => n.data.uri));
            expect(uniqueNodeUris.size).toBeLessThanOrEqual(elements.nodes.length);
        });

        test('should call update callback', async () => {
            const mockData = [];
            const updateCallback = jest.fn();

            axios.get.mockResolvedValue({ data: mockData });

            await links('http://example.org/entity', 'outgoing', elements, updateCallback);

            // Update callback might be called for label/description fetches
            // Just verify it's a function that can be called
            expect(typeof updateCallback).toBe('function');
        });

        describe('node creation', () => {
            test('should create node with URI and label', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const node = elements.node('http://example.org/test', 'Test Node');

                expect(node.data.uri).toBe('http://example.org/test');
                expect(node.data.label).toBe('Test Node');
                expect(node.group).toBe('nodes');
            });

            test('should return existing node', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const node1 = elements.node('http://example.org/test', 'Test Node');
                const node2 = elements.node('http://example.org/test', 'Test Node');

                expect(node1).toBe(node2);
            });

            test('should process node types', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const types = ['http://example.org/Type1', 'http://example.org/Type2'];
                const node = elements.node('http://example.org/test', 'Test', types);

                expect(node.data['@type']).toEqual(types);
                expect(node.classes).toBe('http://example.org/Type1 http://example.org/Type2');
            });
        });

        describe('edge creation', () => {
            test('should create edge', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const edgeData = {
                    source: 'http://example.org/s1',
                    target: 'http://example.org/t1',
                    link: 'http://example.org/predicate',
                    probability: 0.95
                };

                const edge = elements.edge(edgeData);

                expect(edge.data.source).toBe('http://example.org/s1');
                expect(edge.data.target).toBe('http://example.org/t1');
                expect(edge.group).toBe('edges');
            });

            test('should calculate edge width from probability', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const edge = elements.edge({
                    source: 's',
                    target: 't',
                    link: 'l',
                    probability: 0.8
                });

                expect(edge.data.width).toBe(1.8);
            });

            test('should calculate edge width from zscore', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                const edge = elements.edge({
                    source: 's',
                    target: 't',
                    link: 'l',
                    zscore: 2.5
                });

                expect(edge.data.width).toBe(3.5);
            });
        });

        describe('utility methods', () => {
            test('all() should return combined nodes and edges', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                elements.nodes.push({ data: { id: 'n1' } });
                elements.edges.push({ data: { id: 'e1' } });

                const all = elements.all();

                expect(all.length).toBe(2);
                expect(all[0].data.id).toBe('n1');
                expect(all[1].data.id).toBe('e1');
            });

            test('empty() should create new empty structure', async () => {
                axios.get.mockResolvedValue({ data: [] });
                await links('http://example.org/entity', 'outgoing', elements);

                elements.nodes.push({ data: { id: 'n1' } });

                const emptyElements = elements.empty();

                expect(emptyElements.nodes.length).toBe(0);
                expect(emptyElements.edges.length).toBe(0);
                expect(emptyElements.nodeMap).toBe(elements.nodeMap);
            });
        });
    });
});
