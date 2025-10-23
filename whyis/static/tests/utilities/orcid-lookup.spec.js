/**
 * @jest-environment jsdom
 */

import lookupOrcid from '../../js/whyis_vue/utilities/orcid-lookup';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('orcid-lookup utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('lookupOrcid', () => {
    test('should fetch and return ORCID data for valid hyphenated ID', async () => {
      const mockOrcidData = {
        '@graph': [
          {
            '@id': 'http://orcid.org/0000-0001-2345-6789',
            'name': 'Test Researcher',
            'email': 'test@example.com'
          }
        ]
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      const result = await lookupOrcid('0000-0001-2345-6789', 'contactPoint');

      expect(axios.get).toHaveBeenCalledWith(
        '/orcid/0000-0001-2345-6789?view=describe',
        expect.objectContaining({
          headers: { 'Accept': 'application/ld+json' }
        })
      );
      expect(result).toEqual(mockOrcidData['@graph'][0]);
    });

    test('should fetch and return ORCID data for valid unhyphenated ID', async () => {
      const mockOrcidData = {
        '@graph': [
          {
            '@id': 'http://orcid.org/0000000123456789',
            'name': 'Test Researcher'
          }
        ]
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      const result = await lookupOrcid('0000000123456789', 'contactPoint');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toBeDefined();
    });

    test('should return "Invalid" for invalid ORCID ID format', async () => {
      const result = await lookupOrcid('invalid-id', 'contactPoint');

      expect(axios.get).not.toHaveBeenCalled();
      expect(result).toBe('Invalid');
    });

    test('should return "Invalid" for empty ORCID ID', async () => {
      const result = await lookupOrcid('', 'contactPoint');

      expect(result).toBe('Invalid');
    });

    test('should return "Invalid" for ORCID ID with wrong length', async () => {
      const result = await lookupOrcid('0000-0001-2345', 'contactPoint');

      expect(result).toBe('Invalid');
    });

    test('should handle ORCID lookup with different types', async () => {
      const mockOrcidData = {
        '@graph': [
          {
            '@id': 'http://orcid.org/0000-0001-2345-6789',
            'name': 'Test Researcher'
          }
        ]
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      await lookupOrcid('0000-0001-2345-6789', 'author');

      expect(axios.get).toHaveBeenCalled();
    });

    test('should handle response without @graph', async () => {
      const mockOrcidData = {
        '@id': 'http://orcid.org/0000-0001-2345-6789',
        'name': 'Test Researcher'
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      const result = await lookupOrcid('0000-0001-2345-6789', 'contactPoint');

      expect(result).toEqual(mockOrcidData);
    });

    test('should handle empty @graph array for non-contactPoint types', async () => {
      const mockOrcidData = {
        '@graph': []
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      const result = await lookupOrcid('0000-0001-2345-6789', 'author');

      expect(result).toBeUndefined();
    });

    test('should handle ORCID ID with different formatting', async () => {
      const mockOrcidData = {
        '@graph': [
          {
            '@id': 'http://orcid.org/0000-0001-2345-6789',
            'name': 'Test'
          }
        ]
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      // Try with different formats
      await lookupOrcid('(0000)0001-2345-6789', 'contactPoint');
      expect(axios.get).toHaveBeenCalled();
    });

    test('should handle API errors gracefully', async () => {
      axios.get = jest.fn().mockRejectedValue(new Error('Network error'));

      await expect(
        lookupOrcid('0000-0001-2345-6789', 'contactPoint')
      ).rejects.toThrow('Network error');
    });

    test('should validate 16-digit unhyphenated ORCID', async () => {
      const mockOrcidData = {
        '@graph': [
          {
            '@id': 'http://orcid.org/0000-0001-2345-6789',
            'name': 'Test'
          }
        ]
      };

      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      const result = await lookupOrcid('0000000123456789', 'author');

      expect(axios.get).toHaveBeenCalled();
    });

    test('should use Accept header for JSON-LD', async () => {
      const mockOrcidData = { '@graph': [{ '@id': 'http://orcid.org/0000-0001-2345-6789' }] };
      axios.get = jest.fn().mockResolvedValue({ data: mockOrcidData });

      await lookupOrcid('0000-0001-2345-6789', 'author');

      expect(axios.get).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: { 'Accept': 'application/ld+json' }
        })
      );
    });
  });
});
