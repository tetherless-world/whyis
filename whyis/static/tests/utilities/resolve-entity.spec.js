/**
 * Tests for resolve-entity utility
 * @jest-environment jsdom
 */

import axios from 'axios';
import { resolveEntity } from '@/utilities/resolve-entity';

// Mock axios
jest.mock('axios');

describe('resolve-entity', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
    });

    describe('resolveEntity', () => {
        test('should resolve entities with query', async () => {
            const mockData = [
                { node: 'http://example.org/1', label: 'Test Entity' },
                { node: 'http://example.org/2', label: 'Another Entity' }
            ];
            
            axios.get.mockResolvedValue({
                data: mockData
            });

            const result = await resolveEntity('test');
            
            expect(result).toHaveLength(2);
            expect(result[0].label).toBe('Test Entity');
            expect(result[0].value).toBe('test entity');
            expect(axios.get).toHaveBeenCalledWith(
                'http://localhost/',
                {
                    params: { view: 'resolve', term: 'test*' },
                    responseType: 'json'
                }
            );
        });

        test('should add wildcard to query', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await resolveEntity('search');
            
            expect(axios.get).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    params: expect.objectContaining({
                        term: 'search*'
                    })
                })
            );
        });

        test('should include type parameter when provided', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await resolveEntity('test', 'http://example.org/Type');
            
            expect(axios.get).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    params: {
                        view: 'resolve',
                        term: 'test*',
                        type: 'http://example.org/Type'
                    }
                })
            );
        });

        test('should not include type parameter when undefined', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await resolveEntity('test');
            
            const callParams = axios.get.mock.calls[0][1].params;
            expect(callParams).not.toHaveProperty('type');
        });

        test('should handle entities without labels', async () => {
            const mockData = [
                { node: 'http://example.org/1' }
            ];
            
            axios.get.mockResolvedValue({ data: mockData });

            const result = await resolveEntity('test');
            
            expect(result[0].value).toBe('');
        });

        test('should add lowercase value to each result', async () => {
            const mockData = [
                { node: 'http://example.org/1', label: 'UPPERCASE' },
                { node: 'http://example.org/2', label: 'MixedCase' }
            ];
            
            axios.get.mockResolvedValue({ data: mockData });

            const result = await resolveEntity('test');
            
            expect(result[0].value).toBe('uppercase');
            expect(result[1].value).toBe('mixedcase');
        });

        test('should handle empty response', async () => {
            axios.get.mockResolvedValue({ data: [] });

            const result = await resolveEntity('test');
            
            expect(result).toEqual([]);
        });

        test('should handle null or undefined response data', async () => {
            axios.get.mockResolvedValue({ data: null });

            const result = await resolveEntity('test');
            
            expect(result).toEqual([]);
        });

        test('should handle API errors gracefully', async () => {
            const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
            axios.get.mockRejectedValue(new Error('Network error'));

            const result = await resolveEntity('test');
            
            expect(result).toEqual([]);
            expect(consoleErrorSpy).toHaveBeenCalled();
            
            consoleErrorSpy.mockRestore();
        });

        test('should use custom root URL when provided', async () => {
            axios.get.mockResolvedValue({ data: [] });

            await resolveEntity('test', undefined, 'http://custom.example.org/');
            
            expect(axios.get).toHaveBeenCalledWith(
                'http://custom.example.org/',
                expect.any(Object)
            );
        });

        test('should preserve all properties from response', async () => {
            const mockData = [
                {
                    node: 'http://example.org/1',
                    label: 'Test',
                    prefLabel: 'Test Label',
                    types: ['http://example.org/Type']
                }
            ];
            
            axios.get.mockResolvedValue({ data: mockData });

            const result = await resolveEntity('test');
            
            expect(result[0]).toMatchObject({
                node: 'http://example.org/1',
                label: 'Test',
                prefLabel: 'Test Label',
                types: ['http://example.org/Type'],
                value: 'test'
            });
        });
    });
});
