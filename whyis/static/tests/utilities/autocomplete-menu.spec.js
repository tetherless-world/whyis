/**
 * @jest-environment jsdom
 */

import { processAutocompleteMenu, getAuthorList, getOrganizationlist } from '../../js/whyis_vue/utilities/autocomplete-menu';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('autocomplete-menu utilities', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  describe('processAutocompleteMenu', () => {
    test('should style autocomplete menu when it exists', () => {
      const menuElement = document.createElement('div');
      menuElement.className = 'md-menu-content-bottom-start';
      document.body.appendChild(menuElement);

      const result = processAutocompleteMenu();

      expect(menuElement.style['z-index']).toBe('12');
      expect(menuElement.style['width']).toBe('75%');
      expect(menuElement.style['max-width']).toBe('75%');
      expect(result).toBe(true);
    });

    test('should return undefined when no menu element exists', () => {
      const result = processAutocompleteMenu();
      expect(result).toBeUndefined();
    });

    test('should only style the first menu element', () => {
      const menu1 = document.createElement('div');
      menu1.className = 'md-menu-content-bottom-start';
      const menu2 = document.createElement('div');
      menu2.className = 'md-menu-content-bottom-start';
      
      document.body.appendChild(menu1);
      document.body.appendChild(menu2);

      processAutocompleteMenu();

      expect(menu1.style['z-index']).toBe('12');
      expect(menu2.style['z-index']).toBe('');
    });

    test('should not throw error when called multiple times', () => {
      const menuElement = document.createElement('div');
      menuElement.className = 'md-menu-content-bottom-start';
      document.body.appendChild(menuElement);

      expect(() => {
        processAutocompleteMenu();
        processAutocompleteMenu();
        processAutocompleteMenu();
      }).not.toThrow();
    });
  });

  describe('getAuthorList', () => {
    test('should fetch authors from both FOAF and Schema.org types', async () => {
      const foafAuthors = [
        { id: '1', name: 'John Doe', score: 0.9 }
      ];
      const schemaAuthors = [
        { id: '2', name: 'Jane Smith', score: 0.8 }
      ];

      axios.all = jest.fn(() => Promise.resolve([
        { data: foafAuthors },
        { data: schemaAuthors }
      ]));
      axios.get = jest.fn();

      const result = await getAuthorList('john');

      expect(axios.get).toHaveBeenCalledWith(
        '/?term=john*&view=resolve&type=http://xmlns.com/foaf/0.1/Person'
      );
      expect(axios.get).toHaveBeenCalledWith(
        '/?term=john*&view=resolve&type=http://schema.org/Person'
      );
      
      expect(result).toHaveLength(2);
    });

    test('should combine and sort results by score', async () => {
      const foafAuthors = [
        { id: '1', name: 'Low Score', score: 0.3 }
      ];
      const schemaAuthors = [
        { id: '2', name: 'High Score', score: 0.9 },
        { id: '3', name: 'Medium Score', score: 0.5 }
      ];

      axios.all = jest.fn(() => Promise.resolve([
        { data: foafAuthors },
        { data: schemaAuthors }
      ]));
      axios.get = jest.fn();

      const result = await getAuthorList('test');

      expect(result).toHaveLength(3);
      expect(result[0].score).toBe(0.9);
      expect(result[1].score).toBe(0.5);
      expect(result[2].score).toBe(0.3);
    });

    test('should handle empty results from both APIs', async () => {
      axios.all = jest.fn(() => Promise.resolve([
        { data: [] },
        { data: [] }
      ]));
      axios.get = jest.fn();

      const result = await getAuthorList('nonexistent');

      expect(result).toEqual([]);
    });

    test('should include wildcard in search term', async () => {
      axios.all = jest.fn(() => Promise.resolve([
        { data: [] },
        { data: [] }
      ]));
      axios.get = jest.fn();

      await getAuthorList('smith');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('term=smith*')
      );
    });

    test('should propagate errors from axios', async () => {
      const error = new Error('Network error');
      axios.all = jest.fn(() => Promise.reject(error));
      axios.get = jest.fn();

      await expect(getAuthorList('test')).rejects.toThrow('Network error');
    });

    test('should handle special characters in query', async () => {
      axios.all = jest.fn(() => Promise.resolve([
        { data: [] },
        { data: [] }
      ]));
      axios.get = jest.fn();

      await getAuthorList('O\'Brien');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining("O'Brien")
      );
    });
  });

  describe('getOrganizationlist', () => {
    test('should fetch organizations with correct parameters', async () => {
      const mockOrgs = [
        { id: '1', name: 'Acme Corp' },
        { id: '2', name: 'Tech Inc' }
      ];

      axios.get = jest.fn().mockResolvedValue({ data: mockOrgs });

      const result = await getOrganizationlist('corp');

      expect(axios.get).toHaveBeenCalledWith(
        '/?term=corp*&view=resolve&type=http://schema.org/Organization'
      );
      expect(result).toEqual(mockOrgs);
    });

    test('should include wildcard in search term', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: [] });

      await getOrganizationlist('university');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('term=university*')
      );
    });

    test('should use Schema.org Organization type', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: [] });

      await getOrganizationlist('test');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('type=http://schema.org/Organization')
      );
    });

    test('should return empty array when no organizations found', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: [] });

      const result = await getOrganizationlist('nonexistent');

      expect(result).toEqual([]);
    });

    test('should propagate errors from axios', async () => {
      const error = new Error('API error');
      axios.get = jest.fn().mockRejectedValue(error);

      await expect(getOrganizationlist('test')).rejects.toThrow('API error');
    });

    test('should handle special characters in query', async () => {
      axios.get = jest.fn().mockResolvedValue({ data: [] });

      await getOrganizationlist('R&D Company');

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('R&D Company')
      );
    });
  });
});
