/**
 * @jest-environment jsdom
 */

import { describeNanopub, listNanopubs, lodPrefix } from '../../js/whyis_vue/utilities/nanopub';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('nanopub utilities', () => {
  beforeEach(() => {
    // Set up window globals
    window.ROOT_URL = 'http://localhost/';
    window.LOD_PREFIX = 'http://example.org';
    jest.clearAllMocks();
  });

  describe('lodPrefix', () => {
    test('should return LOD_PREFIX from window', () => {
      expect(lodPrefix()).toBe('http://example.org');
    });

    test('should update when window.LOD_PREFIX changes', () => {
      window.LOD_PREFIX = 'http://newprefix.org';
      expect(lodPrefix()).toBe('http://newprefix.org');
    });
  });

  describe('describeNanopub', () => {
    test('should fetch nanopub description data', async () => {
      const mockData = {
        '@id': 'http://example.org/nanopub/123',
        'title': 'Test Nanopub'
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockData });

      const result = await describeNanopub('http://example.org/nanopub/123');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('about?view=describe&uri=')
      );
      expect(result).toEqual(mockData);
    });

    test('should encode URI parameter', async () => {
      const mockData = { data: 'test' };
      axios.get = jest.fn().mockResolvedValue({ data: mockData });

      const uri = 'http://example.org/resource?param=value&other=test';
      await describeNanopub(uri);

      const callArgs = axios.get.mock.calls[0][0];
      expect(callArgs).toContain(encodeURIComponent(uri));
    });

    test('should log debug information', async () => {
      const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();
      const mockData = { data: 'test' };
      axios.get = jest.fn().mockResolvedValue({ data: mockData });

      await describeNanopub('http://example.org/test');

      expect(consoleSpy).toHaveBeenCalledWith(
        'loading nanopub http://example.org/test'
      );

      consoleSpy.mockRestore();
    });

    test('should handle API errors', async () => {
      axios.get = jest.fn().mockRejectedValue(new Error('API Error'));

      await expect(
        describeNanopub('http://example.org/test')
      ).rejects.toThrow('API Error');
    });
  });

  describe('listNanopubs', () => {
    test('should fetch list of nanopubs for a URI', async () => {
      const mockNanopubs = [
        { '@id': 'nanopub1', 'title': 'First' },
        { '@id': 'nanopub2', 'title': 'Second' }
      ];

      axios.get = jest.fn().mockResolvedValue({ data: mockNanopubs });

      const result = await listNanopubs('http://example.org/resource');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('about?view=nanopublications&uri=')
      );
      expect(result).toEqual(mockNanopubs);
    });

    test('should encode URI parameter in list request', async () => {
      const mockData = [];
      axios.get = jest.fn().mockResolvedValue({ data: mockData });

      const uri = 'http://example.org/resource?param=value';
      await listNanopubs(uri);

      const callArgs = axios.get.mock.calls[0][0];
      expect(callArgs).toContain(encodeURIComponent(uri));
    });

    test('should log debug information on list', async () => {
      const consoleSpy = jest.spyOn(console, 'debug').mockImplementation();
      const mockData = [];
      axios.get = jest.fn().mockResolvedValue({ data: mockData });

      await listNanopubs('http://example.org/test');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    test('should handle empty nanopub list', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: [] });

      const result = await listNanopubs('http://example.org/resource');

      expect(result).toEqual([]);
    });

    test('should handle API errors in list', async () => {
      axios.get = jest.fn().mockRejectedValue(new Error('Network Error'));

      await expect(
        listNanopubs('http://example.org/test')
      ).rejects.toThrow('Network Error');
    });
  });

  describe('integration', () => {
    test('should use consistent URL patterns', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: {} });

      await describeNanopub('http://example.org/test');
      await listNanopubs('http://example.org/test');

      // Both should use ROOT_URL
      expect(axios.get.mock.calls[0][0]).toContain('http://localhost/');
      expect(axios.get.mock.calls[1][0]).toContain('http://localhost/');
    });

    test('should properly encode complex URIs', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: {} });

      const complexUri = 'http://example.org/resource?param=value&other=test#fragment';
      await describeNanopub(complexUri);

      const callArgs = axios.get.mock.calls[0][0];
      expect(callArgs).toContain(encodeURIComponent(complexUri));
    });
  });
});
