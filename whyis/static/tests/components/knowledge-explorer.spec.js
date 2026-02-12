/**
 * Tests for Knowledge Explorer component
 * @jest-environment jsdom
 */

import { mount, createLocalVue } from '@vue/test-utils';
import KnowledgeExplorer from '@/components/knowledge-explorer.vue';
import cytoscape from 'cytoscape';
import { createLinksService } from '@/utilities/kg-links';
import { resolveEntity } from '@/utilities/resolve-entity';

// Create real createGraphElements for tests
const createGraphElements = () => ({
  nodes: [],
  edges: [],
  nodeMap: {},
  edgeMap: {}
});

// Mock dependencies
jest.mock('cytoscape');
jest.mock('cytoscape-fcose', () => ({}));
jest.mock('@/utilities/kg-links');
jest.mock('@/utilities/resolve-entity');
jest.mock('@/utilities/rdf-utils', () => ({
  getSummary: jest.fn((data) => data.summary || 'Test summary')
}));

describe('KnowledgeExplorer', () => {
  let wrapper;
  let localVue;
  let mockCy;
  let mockLinksService;

  beforeEach(() => {
    localVue = createLocalVue();
    
    // Mock cytoscape instance
    mockCy = {
      on: jest.fn(),
      elements: jest.fn(() => ({
        remove: jest.fn(),
        removeClass: jest.fn()
      })),
      add: jest.fn(),
      layout: jest.fn(() => ({
        run: jest.fn()
      })),
      $: jest.fn(() => ({
        map: jest.fn(() => [])
      })),
      remove: jest.fn(),
      destroy: jest.fn()
    };
    
    cytoscape.mockReturnValue(mockCy);
    cytoscape.use = jest.fn();
    
    // Mock links service
    mockLinksService = jest.fn().mockResolvedValue(undefined);
    createLinksService.mockReturnValue(mockLinksService);
    
    // Mock $http
    localVue.prototype.$http = {
      get: jest.fn().mockResolvedValue({ data: 'test data' })
    };
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.destroy();
    }
    jest.clearAllMocks();
  });

  describe('Component Initialization', () => {
    test('should render component', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(wrapper.exists()).toBe(true);
    });

    test('should initialize cytoscape on mount', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(cytoscape).toHaveBeenCalled();
    });

    test('should create links service on mount', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(createLinksService).toHaveBeenCalled();
    });

    test('should destroy cytoscape on unmount', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      wrapper.destroy();
      expect(mockCy.destroy).toHaveBeenCalled();
    });
  });

  describe('Props', () => {
    test('should accept elements prop', () => {
      const elements = {
        nodes: [],
        edges: [],
        nodeMap: {},
        edgeMap: {}
      };
      wrapper = mount(KnowledgeExplorer, {
        localVue,
        propsData: { elements }
      });
      expect(wrapper.props().elements).toBe(elements);
    });

    test('should accept layout prop', () => {
      const layout = { name: 'circle', animate: false };
      wrapper = mount(KnowledgeExplorer, {
        localVue,
        propsData: { layout }
      });
      expect(wrapper.props().layout).toEqual(layout);
    });

    test('should accept title prop', () => {
      wrapper = mount(KnowledgeExplorer, {
        localVue,
        propsData: { title: 'Test Explorer' }
      });
      expect(wrapper.props().title).toBe('Test Explorer');
    });

    test('should accept start prop', () => {
      wrapper = mount(KnowledgeExplorer, {
        localVue,
        propsData: { start: 'http://example.org/entity' }
      });
      expect(wrapper.props().start).toBe('http://example.org/entity');
    });
  });

  describe('Data', () => {
    test('should initialize with default data', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(wrapper.vm.searchText).toBe('');
      expect(wrapper.vm.selectedElements).toEqual([]);
      expect(wrapper.vm.loading).toEqual([]);
      expect(wrapper.vm.probThreshold).toBe(0.93);
    });

    test('should have cy reference after mount', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(wrapper.vm.cy).toBe(mockCy);
    });
  });

  describe('Computed Properties', () => {
    test('hasSelection should be false when nothing selected', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      expect(wrapper.vm.hasSelection).toBe(false);
    });

    test('hasSelection should be true when elements selected', () => {
      wrapper = mount(KnowledgeExplorer, { localVue });
      wrapper.setData({ selectedElements: [{ id: '1' }] });
      expect(wrapper.vm.hasSelection).toBe(true);
    });
  });

  describe('Methods', () => {
    beforeEach(() => {
      wrapper = mount(KnowledgeExplorer, { localVue });
    });

    describe('render', () => {
      test('should update cytoscape elements', () => {
        wrapper.vm.elements = {
          all: jest.fn(() => [{ data: { id: '1' } }])
        };
        
        wrapper.vm.render();
        
        expect(mockCy.elements).toHaveBeenCalled();
        expect(mockCy.add).toHaveBeenCalled();
        expect(mockCy.layout).toHaveBeenCalled();
      });

      test('should not render if cy is null', () => {
        wrapper.vm.cy = null;
        wrapper.vm.render();
        // Should not throw error
      });
    });

    describe('updateSelection', () => {
      test('should update selected elements', () => {
        const mockElements = [
          { id: () => '1', data: () => ({ id: '1', label: 'Node 1' }) }
        ];
        
        mockCy.$ = jest.fn(() => ({
          map: jest.fn((fn) => mockElements.map(fn))
        }));
        
        wrapper.vm.updateSelection();
        
        expect(wrapper.vm.selectedElements.length).toBeGreaterThan(0);
      });
    });

    describe('incomingOutgoing', () => {
      test('should load both incoming and outgoing links', async () => {
        const entities = ['http://example.org/entity1'];
        wrapper.vm.elements = createGraphElements();
        Object.assign(wrapper.vm.elements, {
          all: jest.fn(() => []),
          empty: jest.fn()
        });
        
        await wrapper.vm.incomingOutgoing(entities);
        
        expect(mockLinksService).toHaveBeenCalledTimes(2);
        expect(mockLinksService).toHaveBeenCalledWith(
          entities[0],
          'incoming',
          expect.objectContaining({
            nodes: expect.any(Array),
            edges: expect.any(Array)
          }),
          expect.any(Function),
          0.93,
          1
        );
      });

      test('should manage loading state', async () => {
        const entities = ['http://example.org/entity1'];
        
        const promise = wrapper.vm.incomingOutgoing(entities);
        expect(wrapper.vm.loading).toContain(entities[0]);
        
        await promise;
        expect(wrapper.vm.loading).not.toContain(entities[0]);
      });

      test('should use selected nodes if no entities provided', async () => {
        mockCy.$ = jest.fn(() => ({
          map: jest.fn(() => ['http://example.org/selected'])
        }));
        
        await wrapper.vm.incomingOutgoing();
        
        expect(mockLinksService).toHaveBeenCalled();
      });
    });

    describe('incoming', () => {
      test('should load only incoming links', async () => {
        const entities = ['http://example.org/entity1'];
        wrapper.vm.elements = createGraphElements();
        Object.assign(wrapper.vm.elements, {
          all: jest.fn(() => []),
          empty: jest.fn()
        });
        
        await wrapper.vm.incoming(entities);
        
        expect(mockLinksService).toHaveBeenCalledTimes(1);
        expect(mockLinksService).toHaveBeenCalledWith(
          entities[0],
          'incoming',
          expect.objectContaining({
            nodes: expect.any(Array)
          }),
          expect.any(Function),
          0.93,
          1
        );
      });
    });

    describe('outgoing', () => {
      test('should load only outgoing links', async () => {
        const entities = ['http://example.org/entity1'];
        wrapper.vm.elements = createGraphElements();
        Object.assign(wrapper.vm.elements, {
          all: jest.fn(() => []),
          empty: jest.fn()
        });
        
        await wrapper.vm.outgoing(entities);
        
        expect(mockLinksService).toHaveBeenCalledTimes(1);
        expect(mockLinksService).toHaveBeenCalledWith(
          entities[0],
          'outgoing',
          expect.objectContaining({
            nodes: expect.any(Array)
          }),
          expect.any(Function),
          0.93,
          1
        );
      });
    });

    describe('remove', () => {
      test('should remove selected elements', () => {
        const mockSelected = [
          { id: () => '1', data: { id: '1' } },
          { id: () => '2', data: { id: '2' } }
        ];
        
        mockCy.$ = jest.fn(() => ({
          forEach: jest.fn(fn => mockSelected.forEach(el => fn(el)))
        }));
        
        wrapper.vm.elements = {
          nodes: [
            { data: { id: '1' } },
            { data: { id: '3' } }
          ],
          edges: [
            { data: { id: 'e1', source: '1', target: '3' } },
            { data: { id: 'e2', source: '3', target: '4' } }
          ]
        };
        
        wrapper.vm.remove();
        
        expect(mockCy.remove).toHaveBeenCalled();
        expect(wrapper.vm.elements.nodes.length).toBe(1);
      });
    });

    describe('handleAdd', () => {
      test('should add entities from search', async () => {
        wrapper.setData({ searchText: 'test query' });
        resolveEntity.mockResolvedValue([
          { node: 'http://example.org/result1' },
          { node: 'http://example.org/result2' }
        ]);
        
        await wrapper.vm.handleAdd();
        
        expect(resolveEntity).toHaveBeenCalledWith('test query');
        expect(mockLinksService).toHaveBeenCalled();
      });

      test('should not search if text too short', async () => {
        wrapper.setData({ searchText: 'ab' });
        
        await wrapper.vm.handleAdd();
        
        expect(resolveEntity).not.toHaveBeenCalled();
      });

      test('should add selected entities', async () => {
        wrapper.setData({
          selectedEntities: [
            { node: 'http://example.org/entity1' }
          ]
        });
        
        await wrapper.vm.handleAdd();
        
        expect(mockLinksService).toHaveBeenCalled();
      });
    });
  });

  describe('UI Elements', () => {
    beforeEach(() => {
      wrapper = mount(KnowledgeExplorer, { localVue });
    });

    test('should render graph container', () => {
      expect(wrapper.find('.graph-container').exists()).toBe(true);
    });

    test('should render toolbar', () => {
      expect(wrapper.find('.explorer-toolbar').exists()).toBe(true);
    });

    test('should render search input', () => {
      const searchInput = wrapper.find('.search-input');
      expect(searchInput.exists()).toBe(true);
    });

    test('should render action buttons', () => {
      expect(wrapper.find('button').exists()).toBe(true);
    });

    test('should disable buttons when no selection', () => {
      wrapper.setData({ selectedElements: [] });
      const buttons = wrapper.findAll('button');
      const incomingButton = buttons.filter(w => w.text().includes('Load Incoming')).at(0);
      expect(incomingButton.attributes('disabled')).toBe('disabled');
    });

    test('should enable buttons when items selected', async () => {
      wrapper.setData({ selectedElements: [{ id: '1' }] });
      await wrapper.vm.$nextTick();
      
      const buttons = wrapper.findAll('button');
      const incomingButton = buttons.filter(w => w.text().includes('Load Incoming')).at(0);
      expect(incomingButton.attributes('disabled')).toBeUndefined();
    });

    test('should show details sidebar when elements selected', async () => {
      wrapper.setData({ selectedElements: [{ id: '1', label: 'Test Node' }] });
      await wrapper.vm.$nextTick();
      
      expect(wrapper.find('.details-sidebar').exists()).toBe(true);
    });

    test('should hide details sidebar when nothing selected', async () => {
      wrapper.setData({ selectedElements: [] });
      await wrapper.vm.$nextTick();
      
      expect(wrapper.find('.details-sidebar').exists()).toBe(false);
    });

    test('should show loading indicator when loading', async () => {
      wrapper.setData({ loading: ['http://example.org/entity1'] });
      await wrapper.vm.$nextTick();
      
      expect(wrapper.find('.loading-indicator').exists()).toBe(true);
    });
  });

  describe('Event Handlers', () => {
    beforeEach(() => {
      wrapper = mount(KnowledgeExplorer, { localVue });
    });

    test('should handle search input changes', async () => {
      wrapper.setData({ searchText: 'test search' });
      await wrapper.vm.$nextTick();
      expect(wrapper.vm.searchText).toBe('test search');
    });

    test('should handle probability threshold changes', async () => {
      wrapper.setData({ probThreshold: 0.5 });
      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.probThreshold).toBe(0.5);
    });
  });
});
