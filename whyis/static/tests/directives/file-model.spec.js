/**
 * Tests for file-model directive
 */

import fileModel from '../../js/whyis_vue/directives/file-model';

// Mock the dependencies
jest.mock('../../js/whyis_vue/utilities/formats', () => ({
  getFormatFromFilename: jest.fn((filename) => {
    if (filename.endsWith('.jsonld')) {
      return { mimetype: 'application/ld+json', extension: 'jsonld' };
    }
    if (filename.endsWith('.ttl')) {
      return { mimetype: 'text/turtle', extension: 'ttl' };
    }
    return null;
  })
}));

jest.mock('../../js/whyis_vue/utilities/url-utils', () => ({
  decodeDataURI: jest.fn((dataURI) => ({
    value: 'file content',
    mimetype: 'text/plain'
  }))
}));

describe('file-model directive', () => {
  let el;
  let binding;
  let vnode;
  
  beforeEach(() => {
    // Create a mock file input element
    el = document.createElement('input');
    el.type = 'file';
    document.body.appendChild(el);
    
    // Mock binding object
    binding = {
      value: {
        content: null,
        format: null
      }
    };
    
    // Mock vnode
    vnode = {
      componentInstance: {
        $emit: jest.fn()
      }
    };
  });
  
  afterEach(() => {
    document.body.removeChild(el);
  });
  
  describe('bind', () => {
    it('should add change event listener', () => {
      const addEventListenerSpy = jest.spyOn(el, 'addEventListener');
      
      fileModel.bind(el, binding, vnode);
      
      expect(addEventListenerSpy).toHaveBeenCalledWith('change', expect.any(Function));
    });
    
    it('should handle missing files gracefully', () => {
      fileModel.bind(el, binding, vnode);
      
      // Trigger change event with no files
      const changeEvent = new Event('change');
      Object.defineProperty(changeEvent, 'target', {
        value: { files: [] },
        writable: false
      });
      
      expect(() => {
        el.dispatchEvent(changeEvent);
      }).not.toThrow();
    });
  });
  
  describe('unbind', () => {
    it('should remove event listener', () => {
      const removeEventListenerSpy = jest.spyOn(el, 'removeEventListener');
      
      fileModel.bind(el, binding, vnode);
      fileModel.unbind(el);
      
      expect(removeEventListenerSpy).toHaveBeenCalled();
    });
  });
});
