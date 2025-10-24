/**
 * Tests for ResourceAction component
 * @jest-environment jsdom
 */

import { shallowMount } from '@vue/test-utils';
import ResourceAction from '@/components/resource-action.vue';
import * as labelFetcher from '@/utilities/label-fetcher';

// Mock the label fetcher
jest.mock('@/utilities/label-fetcher');

describe('ResourceAction', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.window.ROOT_URL = 'http://localhost/';
        
        // Setup default mocks
        labelFetcher.getLabelSync.mockReturnValue('Default Label');
        labelFetcher.getLabel.mockResolvedValue('Fetched Label');
    });

    test('should render with required props', () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'edit'
            }
        });

        expect(wrapper.find('a').exists()).toBe(true);
    });

    test('should create correct link URL with action', () => {
        const uri = 'http://example.org/resource/123';
        const action = 'edit';
        const wrapper = shallowMount(ResourceAction, {
            propsData: { uri, action }
        });

        const expectedUrl = `http://localhost/about?uri=${encodeURIComponent(uri)}&view=${encodeURIComponent(action)}`;
        expect(wrapper.find('a').attributes('href')).toBe(expectedUrl);
    });

    test('should use provided label when given', () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'view',
                label: 'Custom Label'
            }
        });

        expect(wrapper.text()).toBe('Custom Label');
    });

    test('should fetch label when not provided', async () => {
        const uri = 'http://example.org/resource/123';
        
        shallowMount(ResourceAction, {
            propsData: {
                uri,
                action: 'edit'
            }
        });

        // Wait for the next tick to allow watch to execute
        await new Promise(resolve => process.nextTick(resolve));

        expect(labelFetcher.getLabel).toHaveBeenCalledWith(uri, 'http://localhost/');
    });

    test('should display fetched label after loading', async () => {
        labelFetcher.getLabel.mockResolvedValue('Loaded Label');
        
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'edit'
            }
        });

        // Wait for the label to be fetched
        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.fetchedLabel).toBe('Loaded Label');
    });

    test('should encode action parameter in URL', () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'custom-view'
            }
        });

        const href = wrapper.find('a').attributes('href');
        expect(href).toContain('view=custom-view');
    });

    test('should handle special characters in action', () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'view&edit'
            }
        });

        const href = wrapper.find('a').attributes('href');
        expect(href).toContain(encodeURIComponent('view&edit'));
    });

    test('should handle label fetch error gracefully', async () => {
        const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
        labelFetcher.getLabel.mockRejectedValue(new Error('Network error'));
        
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'edit'
            }
        });

        await new Promise(resolve => process.nextTick(resolve));
        await wrapper.vm.$nextTick();

        expect(consoleWarnSpy).toHaveBeenCalled();
        consoleWarnSpy.mockRestore();
    });

    test('should update label when URI changes', async () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/1',
                action: 'edit'
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
        shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'edit',
                label: 'Provided Label'
            }
        });

        expect(labelFetcher.getLabel).not.toHaveBeenCalled();
    });

    test('should set title attribute to display label', () => {
        const wrapper = shallowMount(ResourceAction, {
            propsData: {
                uri: 'http://example.org/resource/123',
                action: 'edit',
                label: 'Test Label'
            }
        });

        expect(wrapper.find('a').attributes('title')).toBe('Test Label');
    });

    test('should support different actions', () => {
        const actions = ['edit', 'view', 'delete', 'download'];
        
        actions.forEach(action => {
            const wrapper = shallowMount(ResourceAction, {
                propsData: {
                    uri: 'http://example.org/resource/123',
                    action
                }
            });

            expect(wrapper.find('a').attributes('href')).toContain(`view=${action}`);
        });
    });
});
