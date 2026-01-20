/**
 * Tests for label fetching utility
 * @jest-environment jsdom
 */

import axios from 'axios';
import { 
    getLabel, 
    getLabelSync, 
    clearLabelCache, 
    hasLabel,
    labelFilter 
} from '@/utilities/label-fetcher';

// Mock axios
jest.mock('axios');

describe('label-fetcher', () => {
    beforeEach(() => {
        // Clear cache before each test
        clearLabelCache();
        // Reset mocks
        jest.clearAllMocks();
        // Set up window.ROOT_URL
        global.window.ROOT_URL = 'http://localhost/';
    });

    describe('getLabel', () => {
        test('should fetch and cache label from API', async () => {
            const uri = 'http://example.org/resource/123';
            const expectedLabel = 'Test Resource';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: expectedLabel
            });

            const label = await getLabel(uri);
            
            expect(label).toBe(expectedLabel);
            expect(axios.get).toHaveBeenCalledWith(
                'http://localhost/about',
                {
                    params: { uri, view: 'label' },
                    responseType: 'text'
                }
            );
        });

        test('should use local part as default before fetching', async () => {
            const uri = 'http://example.org/category/TestCategory';
            
            // Create a promise that never resolves to check the initial state
            axios.get.mockReturnValue(new Promise(() => {}));
            
            // Start the fetch (but don't await)
            getLabel(uri);
            
            // Check that local part is available immediately
            expect(getLabelSync(uri)).toBe('TestCategory');
        });

        test('should extract local part from URI with hash', async () => {
            const uri = 'http://example.org/ns#LocalPart';
            
            axios.get.mockReturnValue(new Promise(() => {}));
            getLabel(uri);
            
            expect(getLabelSync(uri)).toBe('LocalPart');
        });

        test('should return cached label on subsequent calls', async () => {
            const uri = 'http://example.org/resource/123';
            const expectedLabel = 'Cached Label';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: expectedLabel
            });

            // First call
            await getLabel(uri);
            
            // Second call should use cache
            const label = await getLabel(uri);
            
            expect(label).toBe(expectedLabel);
            expect(axios.get).toHaveBeenCalledTimes(1);
        });

        test('should handle API errors gracefully', async () => {
            const uri = 'http://example.org/resource/error';
            
            axios.get.mockRejectedValue(new Error('Network error'));
            
            // Suppress console.warn for this test
            const warnSpy = jest.spyOn(console, 'warn').mockImplementation();
            
            const label = await getLabel(uri);
            
            // Should fall back to local part
            expect(label).toBe('error');
            expect(warnSpy).toHaveBeenCalled();
            
            warnSpy.mockRestore();
        });

        test('should use custom root URL when provided', async () => {
            const uri = 'http://example.org/resource/123';
            const customRoot = 'http://custom.example.org/';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: 'Custom Label'
            });

            await getLabel(uri, customRoot);
            
            expect(axios.get).toHaveBeenCalledWith(
                'http://custom.example.org/about',
                expect.any(Object)
            );
        });

        test('should handle concurrent requests for same URI', async () => {
            const uri = 'http://example.org/resource/123';
            const expectedLabel = 'Concurrent Label';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: expectedLabel
            });

            // Make multiple concurrent requests
            const promises = [
                getLabel(uri),
                getLabel(uri),
                getLabel(uri)
            ];
            
            const labels = await Promise.all(promises);
            
            // Should only make one API call
            expect(axios.get).toHaveBeenCalledTimes(1);
            // All should return the same label
            labels.forEach(label => expect(label).toBe(expectedLabel));
        });
    });

    describe('getLabelSync', () => {
        test('should return cached label if available', async () => {
            const uri = 'http://example.org/resource/123';
            const expectedLabel = 'Sync Label';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: expectedLabel
            });

            await getLabel(uri);
            
            expect(getLabelSync(uri)).toBe(expectedLabel);
        });

        test('should return local part if not cached', () => {
            const uri = 'http://example.org/category/UncachedResource';
            
            expect(getLabelSync(uri)).toBe('UncachedResource');
        });
    });

    describe('hasLabel', () => {
        test('should return true if label is cached', async () => {
            const uri = 'http://example.org/resource/123';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: 'Test Label'
            });

            await getLabel(uri);
            
            expect(hasLabel(uri)).toBe(true);
        });

        test('should return false if label is not cached', () => {
            const uri = 'http://example.org/resource/uncached';
            
            expect(hasLabel(uri)).toBe(false);
        });
    });

    describe('clearLabelCache', () => {
        test('should clear all cached labels', async () => {
            const uri1 = 'http://example.org/resource/1';
            const uri2 = 'http://example.org/resource/2';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: 'Label'
            });

            await getLabel(uri1);
            await getLabel(uri2);
            
            expect(hasLabel(uri1)).toBe(true);
            expect(hasLabel(uri2)).toBe(true);
            
            clearLabelCache();
            
            expect(hasLabel(uri1)).toBe(false);
            expect(hasLabel(uri2)).toBe(false);
        });
    });

    describe('labelFilter', () => {
        test('should return local part initially', () => {
            const uri = 'http://example.org/resource/FilterTest';
            
            axios.get.mockReturnValue(new Promise(() => {}));
            
            const result = labelFilter(uri);
            
            expect(result).toBe('FilterTest');
        });

        test('should return cached label when available', async () => {
            const uri = 'http://example.org/resource/123';
            const expectedLabel = 'Filter Label';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: expectedLabel
            });

            await getLabel(uri);
            
            expect(labelFilter(uri)).toBe(expectedLabel);
        });

        test('should be stateful for Vue reactivity', () => {
            expect(labelFilter.$stateful).toBe(true);
        });

        test('should trigger async fetch when called', () => {
            const uri = 'http://example.org/resource/new';
            
            axios.get.mockResolvedValue({
                status: 200,
                data: 'Async Label'
            });

            labelFilter(uri);
            
            expect(axios.get).toHaveBeenCalled();
        });
    });
});
