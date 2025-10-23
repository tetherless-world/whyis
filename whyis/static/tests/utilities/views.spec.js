/**
 * @jest-environment jsdom
 */

import { DEFAULT_VIEWS, VIEW_URIS, getCurrentUri, getCurrentView, getViewUrl, goToView } from '../../js/whyis_vue/utilities/views';

describe('views utility', () => {
  beforeEach(() => {
    // Reset window properties before each test
    delete window.location;
    window.location = { search: '', href: '' };
    window.NODE_URI = 'http://example.org/test-node';
    window.ROOT_URL = 'http://localhost/';
  });

  describe('DEFAULT_VIEWS constant', () => {
    test('should be frozen and contain expected view modes', () => {
      expect(DEFAULT_VIEWS).toEqual({
        NEW: 'new',
        EDIT: 'edit',
        VIEW: 'view'
      });
      expect(Object.isFrozen(DEFAULT_VIEWS)).toBe(true);
    });
  });

  describe('VIEW_URIS constant', () => {
    test('should be frozen and contain expected URIs', () => {
      expect(VIEW_URIS).toEqual({
        CHART_EDITOR: "http://semanticscience.org/resource/Chart",
        SPARQL_TEMPLATES: "http://vocab.rpi.edu/whyis/SparqlTemplate"
      });
      expect(Object.isFrozen(VIEW_URIS)).toBe(true);
    });
  });

  describe('getCurrentUri', () => {
    test('should return the NODE_URI from window', () => {
      window.NODE_URI = 'http://example.org/custom-uri';
      expect(getCurrentUri()).toBe('http://example.org/custom-uri');
    });

    test('should handle undefined NODE_URI', () => {
      delete window.NODE_URI;
      expect(getCurrentUri()).toBeUndefined();
    });
  });

  describe('getCurrentView', () => {
    test('should return view parameter from URL', () => {
      window.location.search = '?view=edit&uri=example';
      expect(getCurrentView()).toBe('edit');
    });

    test('should return null when no view parameter', () => {
      window.location.search = '?uri=example';
      expect(getCurrentView()).toBeNull();
    });

    test('should handle empty query string', () => {
      window.location.search = '';
      expect(getCurrentView()).toBeNull();
    });

    test('should handle multiple parameters', () => {
      window.location.search = '?foo=bar&view=new&baz=qux';
      expect(getCurrentView()).toBe('new');
    });
  });

  describe('getViewUrl', () => {
    test('should construct URL with view parameter', () => {
      const uri = 'http://example.com/resource';
      const url = getViewUrl(uri, 'edit');
      expect(url).toBe('http://localhost/about?view=edit&uri=http%3A%2F%2Fexample.com%2Fresource');
    });

    test('should construct URL without view parameter when view is null', () => {
      const uri = 'http://example.com/resource';
      const url = getViewUrl(uri, null);
      expect(url).toBe('http://localhost/about?uri=http%3A%2F%2Fexample.com%2Fresource');
    });

    test('should URL-encode the URI parameter', () => {
      const uri = 'http://example.com/resource?param=value&other=test';
      const url = getViewUrl(uri, 'view');
      expect(url).toContain('uri=http%3A%2F%2Fexample.com%2Fresource%3Fparam%3Dvalue%26other%3Dtest');
    });

    test('should use ROOT_URL from window', () => {
      window.ROOT_URL = 'https://myapp.com/';
      const url = getViewUrl('http://example.com/test', 'edit');
      expect(url).toContain('https://myapp.com/about');
    });
  });

  describe('goToView', () => {
    test('should set window.location when no args provided', () => {
      const uri = 'http://example.com/resource';
      const result = goToView(uri, 'edit');
      expect(window.location).toBe('http://localhost/about?view=edit&uri=http%3A%2F%2Fexample.com%2Fresource');
    });

    test('should call window.open when args is "open"', () => {
      window.open = jest.fn(() => ({ mockWindow: true }));
      const uri = 'http://example.com/resource';
      const result = goToView(uri, 'view', 'open');
      
      expect(window.open).toHaveBeenCalledWith(
        'http://localhost/about?view=view&uri=http%3A%2F%2Fexample.com%2Fresource',
        '_blank'
      );
      expect(result).toEqual({ mockWindow: true });
    });
  });
});
