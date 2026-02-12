/**
 * Tests for LatestItems component
 * @jest-environment jsdom
 */

import { shallowMount } from '@vue/test-utils';
import LatestItems from '@/components/latest-items.vue';
import axios from 'axios';
import * as labelFetcher from '@/utilities/label-fetcher';

// Mock axios and label-fetcher
jest.mock('axios');
jest.mock('@/utilities/label-fetcher');

describe('LatestItems', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
        
        // Mock moment properly as a function that returns an object
        global.moment = jest.fn((date) => ({
            utc: jest.fn(function() { return this; }),
            local: jest.fn(function() { return this; }),
            fromNow: jest.fn(() => '2 hours ago')
        }));
        global.moment.utc = jest.fn((date) => ({
            local: jest.fn(function() { return this; }),
            fromNow: jest.fn(() => '2 hours ago')
        }));
        
        labelFetcher.getLabel.mockResolvedValue('Test Label');
    });

    test('should render component', () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(LatestItems);

        expect(wrapper.exists()).toBe(true);
    });

    test('should fetch latest items on mount', async () => {
        axios.get.mockResolvedValue({
            data: [
                { about: 'http://example.org/1', updated: '2024-01-01T00:00:00Z' }
            ]
        });

        shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));

        expect(axios.get).toHaveBeenCalledWith(
            'http://localhost/?view=latest',
            {
                responseType: 'json'
            }
        );
    });

    test('should process entities with moment', async () => {
        const mockEntities = [
            { about: 'http://example.org/1', updated: '2024-01-01T00:00:00Z' }
        ];

        axios.get.mockResolvedValue({ data: mockEntities });

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities[0].fromNow).toBe('2 hours ago');
    });

    test('should fetch labels for entities', async () => {
        const mockEntities = [
            { about: 'http://example.org/1', updated: '2024-01-01T00:00:00Z' }
        ];

        axios.get.mockResolvedValue({ data: mockEntities });

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(labelFetcher.getLabel).toHaveBeenCalledWith(
            'http://example.org/1',
            'http://localhost/'
        );
    });

    test('should handle API errors gracefully', async () => {
        const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
        axios.get.mockRejectedValue(new Error('Network error'));

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.error).toBeTruthy();
        expect(wrapper.vm.entities).toEqual([]);
        expect(consoleErrorSpy).toHaveBeenCalled();

        consoleErrorSpy.mockRestore();
    });

    test('should apply limit when specified', async () => {
        const mockEntities = [
            { about: 'http://example.org/1', updated: '2024-01-01T00:00:00Z' },
            { about: 'http://example.org/2', updated: '2024-01-02T00:00:00Z' },
            { about: 'http://example.org/3', updated: '2024-01-03T00:00:00Z' }
        ];

        axios.get.mockResolvedValue({ data: mockEntities });

        const wrapper = shallowMount(LatestItems, {
            propsData: {
                limit: 2
            }
        });

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities).toHaveLength(2);
    });

    test('should not apply limit when not specified', async () => {
        const mockEntities = [
            { about: 'http://example.org/1', updated: '2024-01-01T00:00:00Z' },
            { about: 'http://example.org/2', updated: '2024-01-02T00:00:00Z' },
            { about: 'http://example.org/3', updated: '2024-01-03T00:00:00Z' }
        ];

        axios.get.mockResolvedValue({ data: mockEntities });

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities).toHaveLength(3);
    });

    test('should extract local part from URI', () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(LatestItems);

        expect(wrapper.vm.getLocalPart('http://example.org/resource/123')).toBe('123');
        expect(wrapper.vm.getLocalPart('http://example.org/ns#Term')).toBe('Term');
        expect(wrapper.vm.getLocalPart('')).toBe('');
    });

    test('should handle empty results', async () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities).toEqual([]);
    });

    test('should handle entities without updated timestamp', async () => {
        const mockEntities = [
            { about: 'http://example.org/1' }
        ];

        axios.get.mockResolvedValue({ data: mockEntities });

        const wrapper = shallowMount(LatestItems);

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.entities[0].fromNow).toBeUndefined();
    });

    test('should return correct URL for entity', () => {
        axios.get.mockResolvedValue({ data: [] });

        const wrapper = shallowMount(LatestItems);

        const entity = { about: 'http://example.org/test' };
        expect(wrapper.vm.getURL(entity)).toBe('http://example.org/test');
    });
});
