/**
 * @jest-environment jsdom
 */

import { RDF, RDFS, WHYIS, SCHEMA } from '../../js/whyis_vue/utilities/common-namespaces';

describe('common-namespaces module', () => {
  test('RDF namespace should have correct URI', () => {
    expect(RDF).toBe("http://www.w3.org/1999/02/22-rdf-syntax-ns#");
  });

  test('RDFS namespace should have correct URI', () => {
    expect(RDFS).toBe("http://www.w3.org/2000/01/rdf-schema#");
  });

  test('WHYIS namespace should have correct URI', () => {
    expect(WHYIS).toBe("http://vocab.rpi.edu/whyis/");
  });

  test('SCHEMA namespace should have correct URI', () => {
    expect(SCHEMA).toBe("http://schema.org/");
  });

  test('all namespaces should be strings', () => {
    expect(typeof RDF).toBe('string');
    expect(typeof RDFS).toBe('string');
    expect(typeof WHYIS).toBe('string');
    expect(typeof SCHEMA).toBe('string');
  });

  test('all namespaces should be valid URLs', () => {
    expect(() => new URL(RDF)).not.toThrow();
    expect(() => new URL(RDFS)).not.toThrow();
    expect(() => new URL(WHYIS)).not.toThrow();
    expect(() => new URL(SCHEMA)).not.toThrow();
  });

  test('namespaces should end with appropriate delimiter', () => {
    // Most RDF namespaces end with # or /
    expect(RDF.endsWith('#') || RDF.endsWith('/')).toBe(true);
    expect(RDFS.endsWith('#') || RDFS.endsWith('/')).toBe(true);
    expect(WHYIS.endsWith('#') || WHYIS.endsWith('/')).toBe(true);
    expect(SCHEMA.endsWith('#') || SCHEMA.endsWith('/')).toBe(true);
  });

  test('namespaces should be unique', () => {
    const namespaces = [RDF, RDFS, WHYIS, SCHEMA];
    const uniqueNamespaces = new Set(namespaces);
    expect(uniqueNamespaces.size).toBe(namespaces.length);
  });
});
