import { shallowMount, createLocalVue } from '@vue/test-utils';
import NewNanopub from '@/components/new-nanopub.vue';
import * as formatsModule from '@/utilities/formats';

const localVue = createLocalVue();

jest.mock('@/utilities/formats');

describe('NewNanopub Component', () => {
  let wrapper;
  const mockFormats = [
    { extension: 'ttl', label: 'Turtle', mimetype: 'text/turtle' },
    { extension: 'rdf', label: 'RDF/XML', mimetype: 'application/rdf+xml' },
    { extension: 'jsonld', label: 'JSON-LD', mimetype: 'application/ld+json' }
  ];

  beforeEach(() => {
    formatsModule.getFormatByExtension.mockImplementation((ext) => {
      return mockFormats.find(f => f.extension === ext);
    });
    formatsModule.getFormatFromFilename.mockImplementation((filename) => {
      const ext = filename.split('.').pop();
      return mockFormats.find(f => f.extension === ext);
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    if (wrapper) {
      wrapper.destroy();
    }
  });

  it('renders without crashing', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('initializes with default graph and formats', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    expect(wrapper.vm.currentGraph).toBe('assertion');
    expect(wrapper.vm.graphs).toEqual(['assertion', 'provenance', 'pubinfo']);
    expect(wrapper.vm.formatOptions.length).toBeGreaterThan(0);
  });

  it('displays correct verb prop', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} },
        verb: 'Create'
      }
    });

    const button = wrapper.find('.btn-primary');
    expect(button.text()).toBe('Create');
  });

  it('uses default verb when not provided', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    const button = wrapper.find('.btn-primary');
    expect(button.text()).toBe('Save');
  });

  it('shows cancel button when editing', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} },
        editing: true
      }
    });

    expect(wrapper.findAll('.btn-secondary').length).toBe(1);
  });

  it('hides cancel button when not editing', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} },
        editing: false
      }
    });

    expect(wrapper.findAll('.btn-secondary').length).toBe(0);
  });

  it('enables save button when content is present', async () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    wrapper.setData({ graphContent: 'Some content' });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.canSave).toBe(true);
  });

  it('disables save button when content is empty', async () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: { assertion: '', provenance: '', pubinfo: '' } }
      }
    });

    await wrapper.vm.$nextTick();
    // Component initializes with empty content from nanopub
    expect(wrapper.vm.graphContent).toBe('');
    expect(wrapper.vm.canSave).toBe(false);
  });

  it('disables save button when content is whitespace', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    wrapper.setData({ graphContent: '   \n\t  ' });
    expect(wrapper.vm.canSave).toBe(false);
  });

  it('switches between graphs', async () => {
    const nanopub = {
      resource: {
        assertion: 'assertion content',
        provenance: 'provenance content',
        pubinfo: 'pubinfo content'
      }
    };

    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: { nanopub }
    });

    wrapper.setData({ currentGraph: 'provenance' });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.graphContent).toContain('provenance');
  });

  it('emits save event with nanopub', () => {
    const nanopub = { resource: {} };
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: { nanopub }
    });

    wrapper.setData({ graphContent: 'Test content' });
    wrapper.vm.handleSave();

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toBe(nanopub);
  });

  it('updates nanopub resource with graph content on save', () => {
    const nanopub = { resource: {} };
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: { nanopub }
    });

    wrapper.setData({
      currentGraph: 'assertion',
      graphContent: 'Test assertion content'
    });
    wrapper.vm.handleSave();

    expect(nanopub.resource.assertion).toBe('Test assertion content');
  });

  it('clears content after save when not editing', () => {
    const nanopub = { resource: {} };
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub,
        editing: false
      }
    });

    wrapper.setData({ graphContent: 'Test content' });
    wrapper.vm.handleSave();

    expect(wrapper.vm.graphContent).toBe('');
  });

  it('keeps content after save when editing', () => {
    const nanopub = { resource: {} };
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub,
        editing: true
      }
    });

    wrapper.setData({ graphContent: 'Test content' });
    wrapper.vm.handleSave();

    expect(wrapper.vm.graphContent).toBe('Test content');
  });

  it('emits cancel event on cancel', () => {
    const nanopub = { resource: {}, editing: true };
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub,
        editing: true
      }
    });

    wrapper.vm.handleCancel();

    expect(wrapper.emitted('cancel')).toBeTruthy();
    expect(nanopub.editing).toBe(false);
  });

  it('handles file upload', async () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    const fileContent = '@prefix ex: <http://example.org/> .';
    const file = new File([fileContent], 'test.ttl', { type: 'text/turtle' });
    
    const input = wrapper.find('input[type="file"]');
    const event = { target: { files: [file] } };

    // Mock FileReader
    const mockFileReader = {
      readAsText: jest.fn(),
      onload: null,
      onerror: null,
      result: fileContent
    };

    global.FileReader = jest.fn(() => mockFileReader);

    wrapper.vm.handleFileUpload(event);

    // Simulate FileReader onload
    mockFileReader.onload({ target: { result: fileContent } });

    await wrapper.vm.$nextTick();

    expect(wrapper.vm.graphContent).toBe(fileContent);
  });

  it('detects format from filename on file upload', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    wrapper.setData({
      formatOptions: mockFormats,
      selectedFormat: mockFormats[0]
    });

    const fileContent = '<rdf:RDF></rdf:RDF>';
    const file = new File([fileContent], 'test.rdf', { type: 'application/rdf+xml' });

    const mockFileReader = {
      readAsText: jest.fn(),
      onload: null,
      onerror: null,
      result: fileContent
    };

    global.FileReader = jest.fn(() => mockFileReader);

    const event = { target: { files: [file] } };
    wrapper.vm.handleFileUpload(event);
    mockFileReader.onload({ target: { result: fileContent } });

    expect(wrapper.vm.selectedFormat.extension).toBe('rdf');
  });

  it('handles file read error', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    const file = new File(['content'], 'test.ttl');
    const mockFileReader = {
      readAsText: jest.fn(),
      onload: null,
      onerror: null
    };

    global.FileReader = jest.fn(() => mockFileReader);

    const event = { target: { files: [file] } };
    wrapper.vm.handleFileUpload(event);
    mockFileReader.onerror();

    expect(wrapper.vm.error).toBe('Failed to read file');
  });

  it('correctly identifies arrays', () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    expect(wrapper.vm.isArray([1, 2, 3])).toBe(true);
    expect(wrapper.vm.isArray('string')).toBe(false);
    expect(wrapper.vm.isArray(null)).toBe(false);
    expect(wrapper.vm.isArray(undefined)).toBe(false);
    expect(wrapper.vm.isArray({})).toBe(false);
  });

  it('shows error message when present', async () => {
    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: {
        nanopub: { resource: {} }
      }
    });

    wrapper.setData({ error: 'Test error message' });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.error).toBe('Test error message');
  });

  it('loads existing nanopub content', () => {
    const nanopub = {
      resource: {
        assertion: 'existing assertion content'
      }
    };

    wrapper = shallowMount(NewNanopub, {
      localVue,
      propsData: { nanopub }
    });

    expect(wrapper.vm.graphContent).toContain('assertion');
  });
});
