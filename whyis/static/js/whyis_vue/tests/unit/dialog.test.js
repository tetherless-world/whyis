/**
 * Unit tests for Dialog component
 * Tests the dialog utility component used throughout the application
 */

import { describe, it, expect, vi } from 'vitest';
import { shallowMountComponent } from '../helpers/test-utils.js';
import Dialog from '../../components/utils/dialog.vue';

// Mock child components that might not be available in tests
vi.mock('../../components/yasqe.vue', () => ({
  default: { name: 'yasqe', template: '<div class="yasqe-mock"></div>' }
}));
vi.mock('../../components/yasr.vue', () => ({
  default: { name: 'yasr', template: '<div class="yasr-mock"></div>' }
}));

describe('Dialog Component', () => {
  describe('Basic Rendering', () => {
    it('renders dialog component', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        }
      });

      expect(wrapper.find('md-dialog').exists()).toBe(true);
    });

    it('renders dialog with correct props binding', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        }
      });

      const dialog = wrapper.find('md-dialog');
      expect(dialog.attributes(':md-active.sync')).toBe('active');
      expect(dialog.attributes(':md-click-outside-to-close')).toBe('true');
    });

    it('displays dialog title when dialog status is active', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              title: 'Test Dialog Title'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Test Dialog Title');
    });
  });

  describe('Props', () => {
    it('accepts active prop', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        }
      });

      expect(wrapper.vm.active).toBe(true);
    });

    it('handles active prop changes', async () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: false
        }
      });

      expect(wrapper.vm.active).toBe(false);

      await wrapper.setProps({ active: true });
      expect(wrapper.vm.active).toBe(true);
    });
  });

  describe('Dialog States', () => {
    it('shows intro mode when dialog.intro is true', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              intro: true
            },
            introTipScreen: 1
          };
        }
      });

      expect(wrapper.find('.viz-intro').exists()).toBe(true);
      expect(wrapper.text()).toContain('tips');
    });

    it('shows standard dialog when dialog.intro is false', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              intro: false,
              status: true,
              title: 'Standard Dialog'
            }
          };
        }
      });

      expect(wrapper.find('.viz-intro').exists()).toBe(false);
      expect(wrapper.find('.utility-dialog-box_header').exists()).toBe(true);
    });

    it('shows share mode when dialog.share is true', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              share: true,
              title: 'Share Dialog',
              chart: 'http://example.org/chart/123',
              message: 'Share this chart'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Chart Link');
      expect(wrapper.find('md-textarea').exists()).toBe(true);
    });

    it('shows query mode when dialog.query is true', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              query: 'SELECT * WHERE { ?s ?p ?o }',
              message: 'SPARQL Query'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('SPARQL Query');
      expect(wrapper.find('.viz-intro-query').exists()).toBe(true);
    });
  });

  describe('Template Usage Scenarios', () => {
    // Test scenarios based on how the component is used in templates
    it('works as confirmation dialog for deletions', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              delete: true,
              title: 'Delete',
              message: 'Are you sure you want to delete this item?'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Are you sure you want to delete this item?');
      expect(wrapper.text()).toContain('Close');
      expect(wrapper.text()).toContain('Delete');
    });

    it('works as share dialog for charts', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              share: true,
              title: 'Share Chart',
              chart: 'http://example.org/chart/shared/abc123',
              message: 'Use this link to share your chart'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Chart Link');
      expect(wrapper.text()).toContain('Use this link to share your chart');
      
      const textarea = wrapper.find('md-textarea');
      expect(textarea.exists()).toBe(true);
      expect(textarea.attributes('v-model')).toBe('dialog.chart');
    });

    it('works as SPARQL query viewer', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              query: 'PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nSELECT * WHERE { ?s rdf:type ?type }',
              message: 'View generated SPARQL query'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('View generated SPARQL query');
      expect(wrapper.find('.viz-intro-query').exists()).toBe(true);
    });
  });

  describe('Button Actions', () => {
    it('displays close button for informational dialogs', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              share: true,
              title: 'Information',
              message: 'Some information'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Close');
    });

    it('displays action buttons for confirmation dialogs', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              status: true,
              delete: true,
              title: 'Delete Item',
              message: 'Confirm deletion'
            }
          };
        }
      });

      expect(wrapper.text()).toContain('Close');
      expect(wrapper.text()).toContain('Delete Item');
    });
  });

  describe('Intro Mode Navigation', () => {
    it('shows navigation buttons in intro mode', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              intro: true
            },
            introTipScreen: 1
          };
        }
      });

      expect(wrapper.text()).toContain('Skip');
      expect(wrapper.text()).toContain('Next');
    });

    it('shows different buttons for last intro screen', () => {
      const wrapper = shallowMountComponent(Dialog, {
        propsData: {
          active: true
        },
        data() {
          return {
            dialog: {
              intro: true
            },
            introTipScreen: 4 // Last screen
          };
        }
      });

      expect(wrapper.text()).toContain('Previous');
      expect(wrapper.text()).toContain('Close');
      expect(wrapper.text()).not.toContain('Next');
    });
  });
});