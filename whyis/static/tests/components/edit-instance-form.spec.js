import { shallowMount } from '@vue/test-utils';
import EditInstanceForm from '../../js/whyis_vue/components/edit-instance-form.vue';
import axios from 'axios';
import * as idGenerator from '../../js/whyis_vue/utilities/id-generator';
import * as uriResolver from '../../js/whyis_vue/utilities/uri-resolver';
import * as nanopub from '../../js/whyis_vue/utilities/nanopub';

// Mock dependencies
jest.mock('axios');
jest.mock('../../js/whyis_vue/utilities/id-generator');
jest.mock('../../js/whyis_vue/utilities/uri-resolver');
jest.mock('../../js/whyis_vue/utilities/nanopub');

describe('EditInstanceForm', () => {
  let wrapper;
  const defaultProps = {
    nodeUri: 'http://example.org/instance123',
    lodPrefix: 'http://example.org',
    rootUrl: 'http://localhost/'
  };

  const mockInstanceData = [
    {
      '@id': 'http://example.org/instance123',
      '@type': ['http://example.org/TestType'],
      'label': [{ '@value': 'Existing Label' }],
      'description': [{ '@value': 'Existing Description' }]
    }
  ];

  beforeEach(() => {
    // Mock ID generation
    idGenerator.makeID = jest.fn().mockReturnValue('test-id');
    
    // Mock URI resolution
    uriResolver.resolveURI = jest.fn(uri => uri);
    
    // Mock nanopub posting
    nanopub.postNewNanopub = jest.fn().mockResolvedValue({});
    
    // Mock axios
    axios.get = jest.fn().mockResolvedValue({ data: mockInstanceData });
    
    // Mock window.location
    delete window.location;
    window.location = { href: '' };
    
    wrapper = shallowMount(EditInstanceForm, {
      propsData: defaultProps
    });
  });

  afterEach(() => {
    wrapper.destroy();
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    expect(wrapper.find('.edit-instance-form').exists()).toBe(true);
    expect(wrapper.find('form').exists()).toBe(true);
  });

  it('shows loading state initially', () => {
    expect(wrapper.vm.loading).toBe(true);
    expect(wrapper.find('.loading').exists()).toBe(true);
  });

  it('loads instance data on mount', async () => {
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick(); // Wait for async operation
    
    expect(axios.get).toHaveBeenCalledWith(
      'http://localhost/about',
      {
        params: {
          view: 'describe',
          uri: 'http://example.org/instance123'
        }
      }
    );
  });

  it('populates form with loaded data', async () => {
    await wrapper.vm.loadInstanceData();
    
    expect(wrapper.vm.instance['@id']).toBe('http://example.org/instance123');
    expect(wrapper.vm.instance['@type']).toEqual(['http://example.org/TestType']);
    expect(wrapper.vm.instance.label).toEqual([{ '@value': 'Existing Label' }]);
    expect(wrapper.vm.instance.description).toEqual([{ '@value': 'Existing Description' }]);
    expect(wrapper.vm.loading).toBe(false);
  });

  it('handles load error gracefully', async () => {
    axios.get = jest.fn().mockRejectedValue(new Error('Network error'));
    
    await wrapper.vm.loadInstanceData();
    
    expect(wrapper.vm.error).toBe('Network error');
    expect(wrapper.vm.loading).toBe(false);
  });

  it('initializes nanopub with node URI', () => {
    expect(wrapper.vm.nanopub['@id']).toBe('http://example.org/instance123');
    expect(wrapper.vm.nanopub['@graph']['@id']).toBe('http://example.org/instance123');
  });

  it('uses node URI for assertion, provenance, and pubinfo IDs', () => {
    const graph = wrapper.vm.nanopub['@graph'];
    
    expect(graph['np:hasAssertion']['@id']).toBe('http://example.org/instance123_assertion');
    expect(graph['np:hasProvenance']['@id']).toBe('http://example.org/instance123_provenance');
    expect(graph['np:hasPublicationInfo']['@id']).toBe('http://example.org/instance123_pubinfo');
  });

  it('updates references input when changed', async () => {
    wrapper.setData({ referencesInput: 'http://ref1.org, http://ref2.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance.references).toEqual([
      { '@id': 'http://ref1.org' },
      { '@id': 'http://ref2.org' }
    ]);
  });

  it('updates quoted from input when changed', async () => {
    wrapper.setData({ quotedFromInput: 'http://quote.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance['quoted from']).toEqual([
      { '@id': 'http://quote.org' }
    ]);
  });

  it('updates derived from input when changed', async () => {
    wrapper.setData({ derivedFromInput: 'http://source.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance['derived from']).toEqual([
      { '@id': 'http://source.org' }
    ]);
  });

  it('formats URI lists correctly', () => {
    const uris = [
      { '@id': 'http://example1.org' },
      { '@id': 'http://example2.org' }
    ];
    
    const formatted = wrapper.vm.formatURIList(uris);
    expect(formatted).toBe('http://example1.org, http://example2.org');
  });

  it('handles empty URI lists', () => {
    expect(wrapper.vm.formatURIList([])).toBe('');
    expect(wrapper.vm.formatURIList(null)).toBe('');
  });

  it('submits form successfully', async () => {
    await wrapper.vm.loadInstanceData();
    wrapper.vm.instance.label[0]['@value'] = 'Updated Label';
    
    await wrapper.vm.submit();
    
    expect(nanopub.postNewNanopub).toHaveBeenCalledWith(wrapper.vm.nanopub);
    expect(uriResolver.resolveURI).toHaveBeenCalled();
    expect(window.location.href).toContain('/about?uri=');
  });

  it('sets isAbout before submission', async () => {
    await wrapper.vm.loadInstanceData();
    await wrapper.vm.submit();
    
    expect(wrapper.vm.nanopub['@graph'].isAbout).toEqual({
      '@id': wrapper.vm.instance['@id']
    });
  });

  it('handles submission error', async () => {
    await wrapper.vm.loadInstanceData();
    nanopub.postNewNanopub = jest.fn().mockRejectedValue(new Error('Save failed'));
    
    await wrapper.vm.submit();
    
    expect(wrapper.vm.error).toBe('Save failed');
    expect(wrapper.vm.saving).toBe(false);
    expect(window.location.href).toBe('');
  });

  it('disables submit button while saving', async () => {
    await wrapper.vm.loadInstanceData();
    wrapper.setData({ saving: true });
    await wrapper.vm.$nextTick();
    
    const submitButton = wrapper.findAll('button').at(0);
    expect(submitButton.attributes('disabled')).toBe('disabled');
    expect(submitButton.text()).toContain('Saving...');
  });

  it('enables submit button when not saving', async () => {
    await wrapper.vm.loadInstanceData();
    wrapper.setData({ saving: false });
    await wrapper.vm.$nextTick();
    
    const submitButton = wrapper.findAll('button').at(0);
    expect(submitButton.attributes('disabled')).toBeUndefined();
    expect(submitButton.text()).toContain('Save Changes');
  });

  it('emits cancel event when cancel button clicked', async () => {
    await wrapper.vm.loadInstanceData();
    const cancelButton = wrapper.findAll('button').at(1);
    await cancelButton.trigger('click');
    
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  it('displays error message when present', async () => {
    await wrapper.vm.loadInstanceData();
    wrapper.setData({ error: 'Test error' });
    await wrapper.vm.$nextTick();
    
    const errorAlert = wrapper.find('.alert-danger');
    expect(errorAlert.exists()).toBe(true);
    expect(errorAlert.text()).toBe('Test error');
  });

  it('displays type badges when instance has types', async () => {
    await wrapper.vm.loadInstanceData();
    await wrapper.vm.$nextTick();
    
    const typeBadges = wrapper.findAll('.badge');
    expect(typeBadges.length).toBeGreaterThan(0);
  });

  it('handles instance with no label', async () => {
    axios.get = jest.fn().mockResolvedValue({
      data: [{ '@id': 'http://example.org/instance123', '@type': ['Test'] }]
    });
    
    await wrapper.vm.loadInstanceData();
    
    expect(wrapper.vm.instance['@id']).toBe('http://example.org/instance123');
  });

  it('handles instance with no description', async () => {
    axios.get = jest.fn().mockResolvedValue({
      data: [{ '@id': 'http://example.org/instance123', '@type': ['Test'], label: [{ '@value': 'Test' }] }]
    });
    
    await wrapper.vm.loadInstanceData();
    
    expect(wrapper.vm.instance.label).toBeDefined();
    expect(wrapper.vm.instance.description).toBeUndefined();
  });

  it('includes all required context mappings', () => {
    const context = wrapper.vm.nanopub['@context'];
    
    expect(context['@vocab']).toBeDefined();
    expect(context['xsd']).toBeDefined();
    expect(context['np']).toBeDefined();
    expect(context['rdfs']).toBeDefined();
    expect(context['dc']).toBeDefined();
    expect(context['prov']).toBeDefined();
    expect(context['sio']).toBeDefined();
  });

  it('properly uses listify utility', () => {
    const result = wrapper.vm.listify('single value');
    expect(Array.isArray(result)).toBe(true);
    
    const arrayResult = wrapper.vm.listify(['item1', 'item2']);
    expect(arrayResult).toEqual(['item1', 'item2']);
  });

  it('parses URI list with whitespace correctly', () => {
    const parsed = wrapper.vm.parseURIList('  http://a.org  ,  http://b.org  ');
    expect(parsed).toEqual([
      { '@id': 'http://a.org' },
      { '@id': 'http://b.org' }
    ]);
  });

  it('filters out empty URIs from parsed list', () => {
    const parsed = wrapper.vm.parseURIList('http://a.org, , http://b.org');
    expect(parsed).toEqual([
      { '@id': 'http://a.org' },
      { '@id': 'http://b.org' }
    ]);
  });
});
