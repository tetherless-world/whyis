import { shallowMount, createLocalVue } from '@vue/test-utils';
import Nanopubs from '@/components/nanopubs.vue';
import NewNanopub from '@/components/new-nanopub.vue';
import * as nanopubModule from '@/utilities/nanopub';

const localVue = createLocalVue();

// Mock the nanopub utility
jest.mock('@/utilities/nanopub');
jest.mock('@/utilities/label-fetcher');

describe('Nanopubs Component', () => {
  let wrapper;
  const mockNanopubs = [
    {
      '@id': 'http://example.org/nanopub1',
      body: '<p>Nanopub 1 content</p>',
      contributor: 'http://example.org/user1'
    },
    {
      '@id': 'http://example.org/nanopub2',
      body: '<p>Nanopub 2 content</p>',
      contributor: 'http://example.org/user2'
    }
  ];

  const mockUser = {
    uri: 'http://example.org/user1',
    admin: false
  };

  beforeEach(() => {
    nanopubModule.listNanopubs.mockResolvedValue(mockNanopubs);
    nanopubModule.describeNanopub.mockResolvedValue({});
    nanopubModule.postNewNanopub.mockResolvedValue({});
    nanopubModule.deleteNanopub.mockResolvedValue({});
  });

  afterEach(() => {
    jest.clearAllMocks();
    if (wrapper) {
      wrapper.destroy();
    }
  });

  it('renders without crashing', () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });
    expect(wrapper.exists()).toBe(true);
  });

  it('loads nanopubs on mount', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(nanopubModule.listNanopubs).toHaveBeenCalledWith('http://example.org/resource1');
    expect(wrapper.vm.nanopubs).toEqual(mockNanopubs);
  });

  it('shows loading state while loading', () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    wrapper.setData({ loading: true });
    expect(wrapper.find('.loading').exists()).toBe(true);
  });

  it('shows error state on load failure', async () => {
    const error = new Error('Load failed');
    nanopubModule.listNanopubs.mockRejectedValue(error);

    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(wrapper.find('.error').exists()).toBe(true);
    expect(wrapper.vm.error).toContain('Failed to load');
  });

  it('determines if user can edit nanopub', () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const ownNanopub = { contributor: 'http://example.org/user1' };
    const otherNanopub = { contributor: 'http://example.org/user2' };

    expect(wrapper.vm.canEdit(ownNanopub)).toBe(true);
    expect(wrapper.vm.canEdit(otherNanopub)).toBe(false);
  });

  it('allows admin to edit any nanopub', () => {
    const adminUser = { uri: 'http://example.org/admin', admin: 'True' };
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: adminUser
      }
    });

    const anyNanopub = { contributor: 'http://example.org/user2' };
    expect(wrapper.vm.canEdit(anyNanopub)).toBe(true);
  });

  it('disallows edit when user has no uri', () => {
    const noUriUser = { admin: false };
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: noUriUser
      }
    });

    const nanopub = { contributor: 'http://example.org/user1' };
    expect(wrapper.vm.canEdit(nanopub)).toBe(false);
  });

  it('enters edit mode for nanopub', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const nanopub = { '@id': 'http://example.org/nanopub1', editing: false };
    await wrapper.vm.editNanopub(nanopub);

    expect(nanopubModule.describeNanopub).toHaveBeenCalledWith('http://example.org/nanopub1');
    expect(nanopub.editing).toBe(true);
  });

  it('handles save nanopub', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const nanopub = { '@id': 'http://example.org/nanopub1', resource: {} };
    await wrapper.vm.handleSaveNanopub(nanopub);

    expect(nanopubModule.postNewNanopub).toHaveBeenCalledWith(nanopub.resource, nanopub['@context']);
    expect(nanopubModule.listNanopubs).toHaveBeenCalled();
  });

  it('handles create nanopub', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const nanopub = { '@id': null, resource: {} };
    await wrapper.vm.handleCreateNanopub(nanopub);

    expect(nanopubModule.postNewNanopub).toHaveBeenCalledWith(nanopub.resource, nanopub['@context']);
    expect(nanopubModule.listNanopubs).toHaveBeenCalled();
  });

  it('shows delete confirmation modal', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const nanopub = { '@id': 'http://example.org/nanopub1' };
    wrapper.vm.deleteNanopub(nanopub);
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.toDelete).toBe(nanopub);
  });

  it('can cancel delete', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    wrapper.setData({ toDelete: { '@id': 'http://example.org/nanopub1' } });
    await wrapper.vm.$nextTick();
    wrapper.vm.cancelDelete();

    expect(wrapper.vm.toDelete).toBe(null);
  });

  it('confirms and deletes nanopub', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const nanopub = { '@id': 'http://example.org/nanopub1' };
    wrapper.setData({ toDelete: nanopub });
    
    await wrapper.vm.confirmDelete();

    expect(nanopubModule.deleteNanopub).toHaveBeenCalledWith('http://example.org/nanopub1');
    expect(wrapper.vm.toDelete).toBe(null);
    expect(nanopubModule.listNanopubs).toHaveBeenCalled();
  });

  it('hides new nanopub form when disabled', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser,
        disableNanopubing: true
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(wrapper.vm.disableNanopubing).toBe(true);
  });

  it('shows new nanopub form when not disabled', async () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser,
        disableNanopubing: false
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(wrapper.vm.disableNanopubing).toBe(false);
  });

  it('trusts HTML content', () => {
    wrapper = shallowMount(Nanopubs, {
      localVue,
      propsData: {
        resource: 'http://example.org/resource1',
        currentUser: mockUser
      }
    });

    const html = '<p>Test content</p>';
    expect(wrapper.vm.trustHtml(html)).toBe(html);
  });
});
