/**
 * @jest-environment jsdom
 */

import { querySparql } from '../../js/whyis_vue/utilities/sparql';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('sparql utilities', () => {
  beforeEach(() => {
    // Set up global ROOT_URL
    global.ROOT_URL = 'http://localhost/';
    jest.clearAllMocks();
  });

  describe('querySparql', () => {
    test('should execute SPARQL query with correct endpoint', async () => {
      const mockResults = {
        head: { vars: ['subject', 'predicate', 'object'] },
        results: {
          bindings: [
            { subject: { type: 'uri', value: 'http://example.org/s1' } }
          ]
        }
      };

      axios.mockResolvedValue({ data: mockResults });

      const query = 'SELECT * WHERE { ?s ?p ?o } LIMIT 10';
      const result = await querySparql(query);

      expect(axios).toHaveBeenCalledWith({
        method: 'post',
        url: 'http://localhost/sparql',
        data: expect.stringContaining(encodeURIComponent(query)),
        headers: {
          'Accept': 'application/sparql-results+json',
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        withCredentials: true
      });

      expect(result).toEqual(mockResults);
    });

    test('should properly encode SPARQL query in request', async () => {
      axios.mockResolvedValue({ data: {} });

      const query = 'SELECT ?s WHERE { ?s a <http://example.org/Type> }';
      await querySparql(query);

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          data: `query=${encodeURIComponent(query)}`
        })
      );
    });

    test('should use POST method for query', async () => {
      axios.mockResolvedValue({ data: {} });

      await querySparql('SELECT * WHERE { ?s ?p ?o }');

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          method: 'post'
        })
      );
    });

    test('should include credentials in request', async () => {
      axios.mockResolvedValue({ data: {} });

      await querySparql('SELECT * WHERE { ?s ?p ?o }');

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          withCredentials: true
        })
      );
    });

    test('should return query results data', async () => {
      const expectedData = {
        head: { vars: ['count'] },
        results: {
          bindings: [{ count: { type: 'literal', value: '42' } }]
        }
      };

      axios.mockResolvedValue({ data: expectedData });

      const result = await querySparql('SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }');

      expect(result).toEqual(expectedData);
    });

    test('should handle empty results', async () => {
      const emptyResults = {
        head: { vars: [] },
        results: { bindings: [] }
      };

      axios.mockResolvedValue({ data: emptyResults });

      const result = await querySparql('SELECT * WHERE { ?s ?p ?o } LIMIT 0');

      expect(result).toEqual(emptyResults);
    });

    test('should propagate errors from axios', async () => {
      const error = new Error('Network error');
      axios.mockRejectedValue(error);

      await expect(querySparql('SELECT * WHERE { ?s ?p ?o }')).rejects.toThrow('Network error');
    });

    test('should handle complex SPARQL queries', async () => {
      axios.mockResolvedValue({ data: {} });

      const complexQuery = `
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?class (COUNT(?instance) as ?count)
        WHERE {
          ?instance a ?class .
          ?class rdfs:label ?label .
        }
        GROUP BY ?class
        ORDER BY DESC(?count)
        LIMIT 100
      `;

      await querySparql(complexQuery);

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.stringContaining(encodeURIComponent(complexQuery))
        })
      );
    });

    test('should use correct content type header', async () => {
      axios.mockResolvedValue({ data: {} });

      await querySparql('SELECT * WHERE { ?s ?p ?o }');

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
          })
        })
      );
    });

    test('should accept SPARQL JSON results', async () => {
      axios.mockResolvedValue({ data: {} });

      await querySparql('SELECT * WHERE { ?s ?p ?o }');

      expect(axios).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            'Accept': 'application/sparql-results+json'
          })
        })
      );
    });
  });
});
