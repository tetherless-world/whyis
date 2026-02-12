/**
 * Tests for ResourceLink component
 * @jest-environment jsdom
 */

import { shallowMount } from '@vue/test-utils';
import ResourceLink from '@/components/resource-link.vue';
import * as labelFetcher from '@/utilities/label-fetcher';

// Mock the label fetcher
jest.mock('@/utilities/label-fetcher');

describe('ResourceLink', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
        
        // Setup default mocks
        labelFetcher.getLabelSync.mockReturnValue('Default Label');
        labelFetcher.getLabel.mockResolvedValue('Fetched Label');
    });

    test('should render with provided URI', () => {
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123'
            }
        });

        expect(wrapper.find('a').exists()).toBe(true);
    });

    test('should create correct link URL', () => {
        const uri = 'http://example.org/resource/123';
        const wrapper = shallowMount(ResourceLink, {
            propsData: { uri }
        });

        const expectedUrl = `http://localhost/about?uri=${encodeURIComponent(uri)}`;
        expect(wrapper.find('a').attributes('href')).toBe(expectedUrl);
    });

    test('should use provided label when given', () => {
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123',
                label: 'Custom Label'
            }
        });

        expect(wrapper.text()).toBe('Custom Label');
    });

    test('should fetch label when not provided', async () => {
        const uri = 'http://example.org/resource/123';
        
        shallowMount(ResourceLink, {
            propsData: { uri }
        });

        // Wait for the next tick to allow watch to execute
        await new Promise(resolve => process.nextTick(resolve));

        expect(labelFetcher.getLabel).toHaveBeenCalledWith(uri, 'http://localhost/');
    });

    test('should display fetched label after loading', async () => {
        labelFetcher.getLabel.mockResolvedValue('Loaded Label');
        
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123'
            }
        });

        // Wait for the label to be fetched
        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.fetchedLabel).toBe('Loaded Label');
    });

    test('should use sync label as fallback', () => {
        labelFetcher.getLabelSync.mockReturnValue('Sync Label');
        
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123'
            }
        });

        expect(wrapper.text()).toBe('Sync Label');
    });

    test('should handle label fetch error gracefully', async () => {
        const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
        labelFetcher.getLabel.mockRejectedValue(new Error('Network error'));
        
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(consoleWarnSpy).toHaveBeenCalled();
        consoleWarnSpy.mockRestore();
    });

    test('should update label when URI changes', async () => {
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/1'
            }
        });

        await wrapper.setProps({ uri: 'http://example.org/resource/2' });
        await new Promise(resolve => process.nextTick(resolve));

        expect(labelFetcher.getLabel).toHaveBeenCalledWith(
            'http://example.org/resource/2',
            'http://localhost/'
        );
    });

    test('should not fetch label if label prop is provided', () => {
        shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123',
                label: 'Provided Label'
            }
        });

        expect(labelFetcher.getLabel).not.toHaveBeenCalled();
    });

    test('should encode URI in link URL', () => {
        const uri = 'http://example.org/resource?param=value&other=test';
        const wrapper = shallowMount(ResourceLink, {
            propsData: { uri }
        });

        const href = wrapper.find('a').attributes('href');
        expect(href).toContain(encodeURIComponent(uri));
    });

    test('should set title attribute to display label', () => {
        const wrapper = shallowMount(ResourceLink, {
            propsData: {
                uri: 'http://example.org/resource/123',
                label: 'Test Label'
            }
        });

        expect(wrapper.find('a').attributes('title')).toBe('Test Label');
    });
});
