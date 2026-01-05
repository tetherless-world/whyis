/**
 * Tests for SearchResult component
 * @jest-environment jsdom
 */

import { shallowMount } from '@vue/test-utils';
import SearchResult from '@/components/search-result.vue';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('SearchResult', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
        delete global.window.RESULTS;
    });

    test('should render with query prop', () => {
        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test search'
            }
        });

        expect(wrapper.exists()).toBe(true);
    });

    test('should fetch results on mount', async () => {
        axios.get.mockResolvedValue({
            data: [
                { about: 'http://example.org/1', label: 'Test 1' }
            ]
        });

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));

        expect(axios.get).toHaveBeenCalledWith(
            'searchApi',
            {
                params: { query: 'test' },
                responseType: 'json'
            }
        );
    });

    test('should use provided results prop', () => {
        const results = [
            { about: 'http://example.org/1', label: 'Test 1' }
        ];

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test',
                results
            }
        });

        expect(wrapper.vm.entities).toEqual(results);
        expect(axios.get).not.toHaveBeenCalled();
    });

    test('should use global RESULTS variable if available', () => {
        const results = [
            { about: 'http://example.org/1', label: 'Global Result' }
        ];
        global.window.RESULTS = results;

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test'
            }
        });

        expect(wrapper.vm.entities).toEqual(results);
        expect(axios.get).not.toHaveBeenCalled();
    });

    test('should show loading state while fetching', async () => {
        axios.get.mockImplementation(() => new Promise(() => {})); // Never resolves

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test'
            }
        });

        await wrapper.vm.$nextTick();
        await new Promise(resolve => process.nextTick(resolve));

        expect(wrapper.vm.loading).toBe(true);
    });

    test('should handle API errors gracefully', async () => {
        const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
        axios.get.mockRejectedValue(new Error('Network error'));

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.error).toBeTruthy();
        expect(wrapper.vm.entities).toEqual([]);
        expect(consoleErrorSpy).toHaveBeenCalled();

        consoleErrorSpy.mockRestore();
    });

    test('should update results when query changes', async () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'initial'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));

        axios.get.mockClear();
        axios.get.mockResolvedValue({
            data: [{ about: 'http://example.org/1', label: 'New Result' }]
        });

        await wrapper.setProps({ query: 'updated' });
        await new Promise(resolve => process.nextTick(resolve));

        expect(axios.get).toHaveBeenCalledWith(
            'searchApi',
            expect.objectContaining({
                params: { query: 'updated' }
            })
        );
    });

    test('should extract local part from URI', () => {
        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test',
                results: []
            }
        });

        expect(wrapper.vm.getLocalPart('http://example.org/resource/123')).toBe('123');
        expect(wrapper.vm.getLocalPart('http://example.org/ns#Term')).toBe('Term');
        expect(wrapper.vm.getLocalPart('')).toBe('');
    });

    test('should handle empty results', async () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(SearchResult, {
            propsData: {
                query: 'test'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities).toEqual([]);
    });
});
