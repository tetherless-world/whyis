import { createResource } from '@/utilities/resource';

describe('createResource', () => {
    beforeEach(() => {
        // Reset the shared resources storage
        if (createResource.resources) {
            createResource.resources = {};
        }
    });

    describe('Resource creation', () => {
        it('should create a resource with @id', () => {
            const resource = createResource('http://example.org/resource1');
            expect(resource['@id']).toBe('http://example.org/resource1');
        });

        it('should create a resource with initial values', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [{ '@value': 'value1' }],
                'http://example.org/prop2': [{ '@value': 'value2' }]
            });
            
            expect(resource['@id']).toBe('http://example.org/resource1');
            expect(resource['http://example.org/prop1']).toEqual([{ '@value': 'value1' }]);
            expect(resource['http://example.org/prop2']).toEqual([{ '@value': 'value2' }]);
        });

        it('should handle @graph in initial values', () => {
            const resource = createResource('http://example.org/resource1', {
                '@graph': [
                    { '@id': 'http://example.org/nested1', 'prop': 'value1' },
                    { '@id': 'http://example.org/nested2', 'prop': 'value2' }
                ]
            });
            
            expect(resource['@id']).toBe('http://example.org/resource1');
            expect(resource['@graph']).toBeDefined();
            expect(resource['@graph'].length).toBe(2);
        });
    });

    describe('values() method', () => {
        it('should return empty array for non-existent predicate', () => {
            const resource = createResource('http://example.org/resource1');
            const values = resource.values('http://example.org/nonexistent');
            
            expect(Array.isArray(values)).toBe(true);
            expect(values.length).toBe(0);
        });

        it('should return array for existing predicate', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [{ '@value': 'value1' }]
            });
            
            const values = resource.values('http://example.org/prop1');
            expect(Array.isArray(values)).toBe(true);
            expect(values.length).toBe(1);
            expect(values[0]).toEqual({ '@value': 'value1' });
        });

        it('should convert single value to array', () => {
            const resource = createResource('http://example.org/resource1');
            resource['http://example.org/prop1'] = { '@value': 'value1' };
            
            const values = resource.values('http://example.org/prop1');
            expect(Array.isArray(values)).toBe(true);
            expect(values.length).toBe(1);
        });
    });

    describe('has() method', () => {
        it('should return false for non-existent predicate', () => {
            const resource = createResource('http://example.org/resource1');
            expect(resource.has('http://example.org/nonexistent')).toBe(false);
        });

        it('should return true for existing predicate', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [{ '@value': 'value1' }]
            });
            
            expect(resource.has('http://example.org/prop1')).toBe(true);
        });

        it('should check for specific object value with @id', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [
                    { '@id': 'http://example.org/obj1' },
                    { '@id': 'http://example.org/obj2' }
                ]
            });
            
            const matches = resource.has('http://example.org/prop1', { '@id': 'http://example.org/obj1' });
            expect(matches.length).toBe(1);
            expect(matches[0]['@id']).toBe('http://example.org/obj1');
        });

        it('should check for specific object value with @value', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [
                    { '@value': 'value1' },
                    { '@value': 'value2' }
                ]
            });
            
            const matches = resource.has('http://example.org/prop1', { '@value': 'value1' });
            expect(matches.length).toBe(1);
            expect(matches[0]['@value']).toBe('value1');
        });

        it('should check for specific plain value', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [
                    { '@value': 'value1' },
                    { '@value': 'value2' }
                ]
            });
            
            const matches = resource.has('http://example.org/prop1', 'value1');
            expect(matches.length).toBe(1);
        });
    });

    describe('value() method', () => {
        it('should return undefined for non-existent predicate', () => {
            const resource = createResource('http://example.org/resource1');
            expect(resource.value('http://example.org/nonexistent')).toBeUndefined();
        });

        it('should return first value for existing predicate', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [
                    { '@value': 'value1' },
                    { '@value': 'value2' }
                ]
            });
            
            const value = resource.value('http://example.org/prop1');
            expect(value).toEqual({ '@value': 'value1' });
        });
    });

    describe('add() method', () => {
        it('should add value to existing predicate', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [{ '@value': 'value1' }]
            });
            
            resource.add('http://example.org/prop1', { '@value': 'value2' });
            
            const values = resource.values('http://example.org/prop1');
            expect(values.length).toBe(2);
            expect(values[1]).toEqual({ '@value': 'value2' });
        });

        it('should add value to non-existent predicate', () => {
            const resource = createResource('http://example.org/resource1');
            
            resource.add('http://example.org/prop1', { '@value': 'value1' });
            
            const values = resource.values('http://example.org/prop1');
            expect(values.length).toBe(1);
            expect(values[0]).toEqual({ '@value': 'value1' });
        });
    });

    describe('set() method', () => {
        it('should set predicate to single value', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [
                    { '@value': 'value1' },
                    { '@value': 'value2' }
                ]
            });
            
            resource.set('http://example.org/prop1', { '@value': 'new value' });
            
            const values = resource.values('http://example.org/prop1');
            expect(values.length).toBe(1);
            expect(values[0]).toEqual({ '@value': 'new value' });
        });

        it('should create new predicate with set', () => {
            const resource = createResource('http://example.org/resource1');
            
            resource.set('http://example.org/prop1', { '@value': 'value1' });
            
            const values = resource.values('http://example.org/prop1');
            expect(values.length).toBe(1);
            expect(values[0]).toEqual({ '@value': 'value1' });
        });
    });

    describe('del() method', () => {
        it('should delete predicate', () => {
            const resource = createResource('http://example.org/resource1', {
                'http://example.org/prop1': [{ '@value': 'value1' }]
            });
            
            resource.del('http://example.org/prop1');
            
            expect(resource['http://example.org/prop1']).toBeUndefined();
        });

        it('should handle deleting non-existent predicate', () => {
            const resource = createResource('http://example.org/resource1');
            
            expect(() => resource.del('http://example.org/nonexistent')).not.toThrow();
        });
    });

    describe('resource() method - nested resources', () => {
        it('should create nested resource', () => {
            const resource = createResource('http://example.org/resource1');
            const nested = resource.resource('http://example.org/nested1', {
                'prop': 'value'
            });
            
            expect(nested['@id']).toBe('http://example.org/nested1');
            expect(nested['prop']).toBe('value');
            expect(resource['@graph']).toBeDefined();
            expect(resource['@graph'].length).toBe(1);
        });

        it('should reuse existing nested resource', () => {
            const resource = createResource('http://example.org/resource1');
            const nested1 = resource.resource('http://example.org/nested1', {
                'prop1': 'value1'
            });
            const nested2 = resource.resource('http://example.org/nested1', {
                'prop2': 'value2'
            });
            
            expect(nested1).toBe(nested2);
            expect(resource['@graph'].length).toBe(1);
        });

        it('should handle @graph in nested resource values', () => {
            const resource = createResource('http://example.org/resource1');
            const nested = resource.resource('http://example.org/nested1', {
                '@graph': [
                    { '@id': 'http://example.org/nested2', 'prop': 'value2' }
                ]
            });
            
            expect(nested.resource.resources['http://example.org/nested2']).toBeDefined();
        });
    });

    describe('Integration scenarios', () => {
        it('should handle complex resource graphs', () => {
            const resource = createResource('urn:nanopub', {
                '@type': 'http://www.nanopub.org/nschema#Nanopublication'
            });
            
            const assertion = resource.resource('urn:assertion', {
                '@type': 'http://www.nanopub.org/nschema#Assertion'
            });
            
            resource['http://www.nanopub.org/nschema#hasAssertion'] = assertion;
            
            expect(resource['@id']).toBe('urn:nanopub');
            expect(resource['@graph'].length).toBe(1);
            expect(assertion['@id']).toBe('urn:assertion');
        });

        it('should support chaining operations', () => {
            const resource = createResource('http://example.org/resource1');
            resource.add('http://example.org/prop1', { '@value': 'value1' });
            resource.add('http://example.org/prop1', { '@value': 'value2' });
            
            expect(resource.values('http://example.org/prop1').length).toBe(2);
            expect(resource.value('http://example.org/prop1')['@value']).toBe('value1');
            expect(resource.has('http://example.org/prop1')).toBe(true);
        });
    });
});
