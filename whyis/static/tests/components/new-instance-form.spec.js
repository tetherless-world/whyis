import { shallowMount } from '@vue/test-utils';
import NewInstanceForm from '../../js/whyis_vue/components/new-instance-form.vue';
import * as idGenerator from '../../js/whyis_vue/utilities/id-generator';
import * as uriResolver from '../../js/whyis_vue/utilities/uri-resolver';
import * as nanopub from '../../js/whyis_vue/utilities/nanopub';

// Mock dependencies
jest.mock('../../js/whyis_vue/utilities/id-generator');
jest.mock('../../js/whyis_vue/utilities/uri-resolver');
jest.mock('../../js/whyis_vue/utilities/nanopub');

describe('NewInstanceForm', () => {
  let wrapper;
  const defaultProps = {
    nodeType: 'http://example.org/TestType',
    lodPrefix: 'http://example.org',
    rootUrl: 'http://localhost/'
  };

  beforeEach(() => {
    // Mock ID generation
    idGenerator.makeID = jest.fn()
      .mockReturnValueOnce('test-np-id')
      .mockReturnValueOnce('test-instance-id');
    
    // Mock URI resolution
    uriResolver.resolveURI = jest.fn(uri => uri);
    
    // Mock nanopub posting
    nanopub.postNewNanopub = jest.fn().mockResolvedValue({});
    
    // Mock window.location
    delete window.location;
    window.location = { href: '' };
    
    wrapper = shallowMount(NewInstanceForm, {
      propsData: defaultProps
    });
  });

  afterEach(() => {
    wrapper.destroy();
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    expect(wrapper.find('.new-instance-form').exists()).toBe(true);
    expect(wrapper.find('form').exists()).toBe(true);
  });

  it('initializes nanopub structure correctly', () => {
    expect(wrapper.vm.nanopub['@id']).toBe('urn:test-np-id');
    expect(wrapper.vm.nanopub['@context']['@vocab']).toBe('http://example.org/');
    expect(wrapper.vm.instance['@id']).toBe('test-instance-id');
    expect(wrapper.vm.instance['@type']).toEqual(['http://example.org/TestType']);
  });

  it('has correct form fields', () => {
    const inputs = wrapper.findAll('input[type="text"]');
    const textareas = wrapper.findAll('textarea');
    
    expect(inputs.length).toBeGreaterThan(0);
    expect(textareas.length).toBeGreaterThan(0);
  });

  it('updates instance label when input changes', async () => {
    const labelInput = wrapper.findAll('input').at(1);
    await labelInput.setValue('Test Label');
    
    expect(wrapper.vm.instance.label['@value']).toBe('Test Label');
  });

  it('updates instance description when textarea changes', async () => {
    const descTextarea = wrapper.find('textarea');
    await descTextarea.setValue('Test Description');
    
    expect(wrapper.vm.instance.description['@value']).toBe('Test Description');
  });

  it('parses references input correctly', async () => {
    wrapper.setData({ referencesInput: 'http://ref1.org, http://ref2.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance.references).toEqual([
      { '@id': 'http://ref1.org' },
      { '@id': 'http://ref2.org' }
    ]);
  });

  it('parses quoted from input correctly', async () => {
    wrapper.setData({ quotedFromInput: 'http://quote1.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance['quoted from']).toEqual([
      { '@id': 'http://quote1.org' }
    ]);
  });

  it('parses derived from input correctly', async () => {
    wrapper.setData({ derivedFromInput: 'http://source1.org, http://source2.org, http://source3.org' });
    await wrapper.vm.$nextTick();
    
    expect(wrapper.vm.provenance['derived from']).toEqual([
      { '@id': 'http://source1.org' },
      { '@id': 'http://source2.org' },
      { '@id': 'http://source3.org' }
    ]);
  });

  it('handles empty URI inputs', () => {
    wrapper.setData({ referencesInput: '' });
    expect(wrapper.vm.provenance.references).toEqual([]);
    
    wrapper.setData({ referencesInput: '   ' });
    expect(wrapper.vm.provenance.references).toEqual([]);
  });

  it('trims whitespace from URIs', async () => {
    wrapper.setData({ referencesInput: '  http://ref1.org  ,  http://ref2.org  ' });
    await wrapper.vm.$nextTick(); // Wait for watcher to process
    expect(wrapper.vm.provenance.references).toEqual([
      { '@id': 'http://ref1.org' },
      { '@id': 'http://ref2.org' }
    ]);
  });

  it('submits form successfully', async () => {
    wrapper.vm.instance.label['@value'] = 'Test Instance';
    wrapper.vm.instance.description['@value'] = 'Test Description';
    
    await wrapper.vm.submit();
    
    expect(nanopub.postNewNanopub).toHaveBeenCalledWith(wrapper.vm.nanopub);
    expect(uriResolver.resolveURI).toHaveBeenCalled();
    expect(window.location.href).toContain('/about?uri=');
  });

  it('sets isAbout before submission', async () => {
    await wrapper.vm.submit();
    
    expect(wrapper.vm.nanopub['@graph'].isAbout).toEqual({
      '@id': wrapper.vm.instance['@id']
    });
  });

  it('handles submission error', async () => {
    nanopub.postNewNanopub = jest.fn().mockRejectedValue(new Error('Network error'));
    
    await wrapper.vm.submit();
    
    expect(wrapper.vm.error).toBe('Network error');
    expect(wrapper.vm.loading).toBe(false);
    expect(window.location.href).toBe('');
  });

  it('disables submit button while loading', async () => {
    wrapper.setData({ loading: true });
    await wrapper.vm.$nextTick();
    
    const submitButton = wrapper.findAll('button').at(0);
    expect(submitButton.attributes('disabled')).toBe('disabled');
    expect(submitButton.text()).toContain('Creating...');
  });

  it('enables submit button when not loading', async () => {
    wrapper.setData({ loading: false });
    await wrapper.vm.$nextTick();
    
    const submitButton = wrapper.findAll('button').at(0);
    expect(submitButton.attributes('disabled')).toBeUndefined();
    expect(submitButton.text()).toContain('Create Instance');
  });

  it('emits cancel event when cancel button clicked', async () => {
    const cancelButton = wrapper.findAll('button').at(1);
    await cancelButton.trigger('click');
    
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  it('displays error message when present', async () => {
    wrapper.setData({ error: 'Test error message' });
    await wrapper.vm.$nextTick();
    
    const errorAlert = wrapper.find('.alert-danger');
    expect(errorAlert.exists()).toBe(true);
    expect(errorAlert.text()).toBe('Test error message');
  });

  it('hides error message when null', () => {
    wrapper.setData({ error: null });
    expect(wrapper.find('.alert-danger').exists()).toBe(false);
  });

  it('uses default node type when not provided', () => {
    const wrapperNoType = shallowMount(NewInstanceForm, {
      propsData: {
        lodPrefix: 'http://example.org',
        rootUrl: 'http://localhost/'
      }
    });
    
    expect(wrapperNoType.vm.instance['@type']).toEqual(['http://www.w3.org/2002/07/owl#Thing']);
    wrapperNoType.destroy();
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

  it('includes all nanopub graphs', () => {
    const graph = wrapper.vm.nanopub['@graph'];
    
    expect(graph['np:hasAssertion']).toBeDefined();
    expect(graph['np:hasProvenance']).toBeDefined();
    expect(graph['np:hasPublicationInfo']).toBeDefined();
  });

  it('properly structures assertion graph', () => {
    const assertion = wrapper.vm.nanopub['@graph']['np:hasAssertion'];
    
    expect(assertion['@type']).toBe('np:Assertion');
    expect(assertion['@graph']).toBeDefined();
    expect(assertion['@graph']['@id']).toBeDefined();
    expect(assertion['@graph']['@type']).toBeDefined();
  });
});
