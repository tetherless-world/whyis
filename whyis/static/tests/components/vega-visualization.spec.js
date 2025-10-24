import { mount } from '@vue/test-utils';
import VegaVisualization from '@/components/vega-visualization.vue';

describe('VegaVisualization', () => {
    let mockVegaEmbed;
    let mockView;

    beforeEach(() => {
        // Mock the vega-embed library
        mockView = {
            finalize: jest.fn()
        };

        mockVegaEmbed = jest.fn().mockResolvedValue({
            view: mockView,
            spec: {}
        });

        global.window.vegaEmbed = mockVegaEmbed;
    });

    afterEach(() => {
        delete global.window.vegaEmbed;
        jest.clearAllMocks();
    });

    describe('Component rendering', () => {
        it('should render container div', () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json',
                width: 400,
                height: 200
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            expect(wrapper.find('.vega-container').exists()).toBe(true);
        });

        it('should call vegaEmbed on mount', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json',
                width: 400,
                height: 200
            };

            mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalled();
        });

        it('should pass spec to vegaEmbed', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json',
                width: 400,
                height: 200,
                data: [{ name: 'table', values: [1, 2, 3] }]
            };

            mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalledWith(
                expect.any(HTMLElement),
                spec,
                expect.objectContaining({ renderer: 'svg' })
            );
        });
    });

    describe('Props handling', () => {
        it('should use default svg renderer', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalledWith(
                expect.any(HTMLElement),
                spec,
                expect.objectContaining({ renderer: 'svg' })
            );
        });

        it('should accept custom options', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };
            const opt = {
                renderer: 'canvas',
                actions: false
            };

            mount(VegaVisualization, {
                propsData: { spec, opt }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalledWith(
                expect.any(HTMLElement),
                spec,
                expect.objectContaining({ renderer: 'canvas', actions: false })
            );
        });

        it('should call then callback if provided', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };
            const thenCallback = jest.fn();

            mount(VegaVisualization, {
                propsData: { spec, then: thenCallback }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(thenCallback).toHaveBeenCalledWith({
                view: mockView,
                spec: {}
            });
        });
    });

    describe('Spec changes', () => {
        it('should re-render when spec changes', async () => {
            const spec1 = {
                $schema: 'https://vega.github.io/schema/vega/v5.json',
                width: 400
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec: spec1 }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalledTimes(1);

            const spec2 = {
                $schema: 'https://vega.github.io/schema/vega/v5.json',
                width: 600
            };

            await wrapper.setProps({ spec: spec2 });
            await new Promise(resolve => setTimeout(resolve, 10));

            expect(mockVegaEmbed).toHaveBeenCalledTimes(2);
        });
    });

    describe('Events', () => {
        it('should emit rendered event on successful render', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(wrapper.emitted('rendered')).toBeTruthy();
            expect(wrapper.emitted('rendered')[0]).toEqual([{
                view: mockView,
                spec: {}
            }]);
        });

        it('should emit error event on render failure', async () => {
            const errorMessage = 'Render failed';
            mockVegaEmbed.mockRejectedValue(new Error(errorMessage));

            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(wrapper.emitted('error')).toBeTruthy();
            expect(wrapper.emitted('error')[0][0].message).toBe(errorMessage);
        });
    });

    describe('Cleanup', () => {
        it('should finalize view on component destroy', async () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            wrapper.destroy();

            expect(mockView.finalize).toHaveBeenCalled();
        });

        it('should handle destroy when view is null', () => {
            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            // Destroy immediately before vegaEmbed completes
            expect(() => wrapper.destroy()).not.toThrow();
        });
    });

    describe('Error handling', () => {
        it('should handle missing vegaEmbed gracefully', async () => {
            delete global.window.vegaEmbed;

            const spec = {
                $schema: 'https://vega.github.io/schema/vega/v5.json'
            };

            const wrapper = mount(VegaVisualization, {
                propsData: { spec }
            });

            await new Promise(resolve => setTimeout(resolve, 10));

            expect(wrapper.emitted('error')).toBeTruthy();
        });

        it('should handle null spec', async () => {
            const wrapper = mount(VegaVisualization, {
                propsData: { spec: {} }
            });

            await wrapper.setProps({ spec: null });
            await new Promise(resolve => setTimeout(resolve, 10));

            // Should not crash
            expect(wrapper.exists()).toBe(true);
        });
    });
});
