/**
 * Unit tests for UploadKnowledge component
 * Tests the knowledge upload dialog component used in the main navigation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { shallowMountComponent, flushPromises } from '../helpers/test-utils.js';
import UploadKnowledge from '../../components/upload-knowledge.vue';

// Mock axios for HTTP requests
const mockAxios = vi.fn(() => Promise.resolve({ data: { success: true } }));

// Mock window.location.reload
const mockReload = vi.fn();

describe('UploadKnowledge Component', () => {
  beforeEach(() => {
    // Mock global ROOT_URL
    global.ROOT_URL = 'http://example.org/';
    
    // Mock axios
    global.axios = mockAxios;
    
    // Mock alert
    global.alert = vi.fn();
    
    // Reset mocks
    mockAxios.mockClear();
    global.alert.mockClear();
  });

  describe('Basic Rendering', () => {
    it('renders dialog with correct title', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      expect(wrapper.find('md-dialog').exists()).toBe(true);
      expect(wrapper.find('md-dialog-title').text()).toBe('Upload Knowledge');
    });

    it('renders file input field', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      expect(wrapper.find('md-file').exists()).toBe(true);
      expect(wrapper.text()).toContain('RDF File');
    });

    it('renders format selection field', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      expect(wrapper.find('md-select').exists()).toBe(true);
      expect(wrapper.text()).toContain('Format');
    });

    it('renders cancel and add buttons', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      const buttons = wrapper.findAll('md-button');
      expect(buttons.length).toBe(2);
      expect(buttons.at(0).text()).toBe('Cancel');
      expect(buttons.at(1).text()).toBe('Add');
    });
  });

  describe('Props', () => {
    it('accepts active prop', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      expect(wrapper.vm.active).toBe(true);
      expect(wrapper.find('md-dialog').attributes(':md-active.sync')).toBe('active');
    });

    it('dialog visibility is controlled by active prop', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: false }
      });

      expect(wrapper.vm.active).toBe(false);
    });
  });

  describe('Data Properties', () => {
    it('initializes with correct default data', () => {
      const wrapper = shallowMountComponent(UploadKnowledge);

      expect(wrapper.vm.formats).toBeInstanceOf(Array);
      expect(wrapper.vm.formats.length).toBeGreaterThan(0);
      expect(wrapper.vm.file).toEqual({ name: '' });
      expect(wrapper.vm.format).toBe(null);
      expect(wrapper.vm.fileobj).toBe('');
      expect(wrapper.vm.status).toBe(false);
      expect(wrapper.vm.awaitingResolve).toBe(false);
      expect(wrapper.vm.awaitingEntity).toBe(false);
    });

    it('includes expected RDF formats', () => {
      const wrapper = shallowMountComponent(UploadKnowledge);

      const formatNames = wrapper.vm.formats.map(f => f.name);
      expect(formatNames).toContain('RDF/XML');
      expect(formatNames).toContain('JSON-LD');
      expect(formatNames).toContain('Turtle');
      expect(formatNames).toContain('TRiG');
      expect(formatNames).toContain('n-Quads');
      expect(formatNames).toContain('N-Triples');
    });

    it('has format_map for lookup', () => {
      const wrapper = shallowMountComponent(UploadKnowledge);

      expect(wrapper.vm.format_map).toBeInstanceOf(Object);
      expect(wrapper.vm.format_map['RDF/XML']).toBeDefined();
      expect(wrapper.vm.format_map['RDF/XML'].mimetype).toBe('application/rdf+xml');
    });
  });

  describe('Methods', () => {
    describe('showDialogBox', () => {
      it('sets active to true', () => {
        const wrapper = shallowMountComponent(UploadKnowledge, {
          propsData: { active: false }
        });

        wrapper.vm.showDialogBox();

        expect(wrapper.vm.active).toBe(true);
      });
    });

    describe('resetDialogBox', () => {
      it('sets active to false and emits update event', () => {
        const wrapper = shallowMountComponent(UploadKnowledge, {
          propsData: { active: true }
        });

        wrapper.vm.resetDialogBox();

        expect(wrapper.vm.active).toBe(false);
        expect(wrapper.emitted('update:active')).toBeTruthy();
        expect(wrapper.emitted('update:active')[0]).toEqual([false]);
      });
    });

    describe('onCancel', () => {
      it('calls resetDialogBox', () => {
        const wrapper = shallowMountComponent(UploadKnowledge, {
          propsData: { active: true }
        });

        const resetSpy = vi.spyOn(wrapper.vm, 'resetDialogBox');

        wrapper.vm.onCancel();

        expect(resetSpy).toHaveBeenCalled();
      });
    });

    describe('onSubmit', () => {
      it('calls save method and reloads page on success', async () => {
        const wrapper = shallowMountComponent(UploadKnowledge, {
          propsData: { active: true }
        });

        const saveSpy = vi.spyOn(wrapper.vm, 'save').mockResolvedValue();
        const resetSpy = vi.spyOn(wrapper.vm, 'resetDialogBox');

        await wrapper.vm.onSubmit();

        expect(saveSpy).toHaveBeenCalled();
        expect(global.window.location.reload).toHaveBeenCalled();
        expect(resetSpy).toHaveBeenCalled();
      });
    });

    describe('handleFileUpload', () => {
      it('sets fileobj from event', () => {
        const wrapper = shallowMountComponent(UploadKnowledge);

        const mockFile = { name: 'test.rdf', size: 1024 };
        const event = [mockFile];

        wrapper.vm.handleFileUpload(event);

        expect(wrapper.vm.fileobj).toBe(mockFile);
      });
    });

    describe('save', () => {
      it('auto-detects format from file extension', async () => {
        const wrapper = shallowMountComponent(UploadKnowledge);

        wrapper.vm.fileobj = { name: 'test.ttl' };
        wrapper.vm.format = null;

        await wrapper.vm.save();

        expect(mockAxios).toHaveBeenCalledWith({
          method: 'post',
          url: 'http://example.org/pub',
          data: wrapper.vm.fileobj,
          headers: { 'Content-Type': 'text/turtle' }
        });
      });

      it('uses selected format when provided', async () => {
        const wrapper = shallowMountComponent(UploadKnowledge);

        wrapper.vm.fileobj = { name: 'test.xml' };
        wrapper.vm.format = 'RDF/XML';

        await wrapper.vm.save();

        expect(mockAxios).toHaveBeenCalledWith({
          method: 'post',
          url: 'http://example.org/pub',
          data: wrapper.vm.fileobj,
          headers: { 'Content-Type': 'application/rdf+xml' }
        });
      });

      it('handles different file extensions correctly', async () => {
        const wrapper = shallowMountComponent(UploadKnowledge);

        // Test JSON-LD
        wrapper.vm.fileobj = { name: 'test.jsonld' };
        wrapper.vm.format = null;

        await wrapper.vm.save();

        expect(mockAxios).toHaveBeenCalledWith(
          expect.objectContaining({
            headers: { 'Content-Type': 'application/ld+json' }
          })
        );
      });

      it('handles errors with alert', async () => {
        const wrapper = shallowMountComponent(UploadKnowledge);

        // Mock axios to throw error
        mockAxios.mockRejectedValueOnce(new Error('Upload failed'));

        wrapper.vm.fileobj = { name: 'test.ttl' };

        await wrapper.vm.save();

        expect(global.alert).toHaveBeenCalledWith(expect.any(Error));
      });
    });
  });

  describe('Format Selection Options', () => {
    it('renders all available format options', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      const options = wrapper.findAll('md-option');
      expect(options.length).toBe(6); // Should have 6 RDF formats

      const optionTexts = options.wrappers.map(option => option.text());
      expect(optionTexts).toContain('RDF/XML');
      expect(optionTexts).toContain('JSON-LD');
      expect(optionTexts).toContain('Turtle');
    });
  });

  describe('Event Handling', () => {
    it('handles file change event', async () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      const handleFileUploadSpy = vi.spyOn(wrapper.vm, 'handleFileUpload');

      // Simulate file input change
      wrapper.find('md-file').vm.$emit('md-change', [{ name: 'test.rdf' }]);

      expect(handleFileUploadSpy).toHaveBeenCalledWith([{ name: 'test.rdf' }]);
    });

    it('handles cancel button click', async () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      const onCancelSpy = vi.spyOn(wrapper.vm, 'onCancel');

      // Simulate cancel button click
      wrapper.findAll('md-button').at(0).vm.$emit('click', { preventDefault: vi.fn() });

      expect(onCancelSpy).toHaveBeenCalled();
    });

    it('handles submit button click', async () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      const onSubmitSpy = vi.spyOn(wrapper.vm, 'onSubmit');

      // Simulate submit button click
      wrapper.findAll('md-button').at(1).vm.$emit('click');

      expect(onSubmitSpy).toHaveBeenCalled();
    });
  });

  describe('Template Usage Scenarios', () => {
    // Test scenarios based on how the component is used in base_vue.html
    it('works as knowledge upload dialog in main navigation', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      // Should be integrated with sync modifier in template
      expect(wrapper.find('md-dialog').attributes(':md-active.sync')).toBe('active');
      expect(wrapper.find('md-dialog').attributes(':md-click-outside-to-close')).toBe('true');
    });

    it('supports complete upload workflow', async () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: false }
      });

      // 1. Show dialog
      wrapper.vm.showDialogBox();
      expect(wrapper.vm.active).toBe(true);

      // 2. Upload file
      const mockFile = { name: 'knowledge.ttl', content: 'turtle content' };
      wrapper.vm.handleFileUpload([mockFile]);
      expect(wrapper.vm.fileobj).toBe(mockFile);

      // 3. Submit
      const saveSpy = vi.spyOn(wrapper.vm, 'save').mockResolvedValue();
      await wrapper.vm.onSubmit();

      expect(saveSpy).toHaveBeenCalled();
      expect(wrapper.vm.active).toBe(false);
    });

    it('integrates with navigation state management', () => {
      const wrapper = shallowMountComponent(UploadKnowledge, {
        propsData: { active: true }
      });

      // Reset should emit update event for parent component
      wrapper.vm.resetDialogBox();

      expect(wrapper.emitted('update:active')).toBeTruthy();
      expect(wrapper.emitted('update:active')[0]).toEqual([false]);
    });
  });
});