/**
 * Tests for ID generator utilities
 * @jest-environment jsdom
 */

import { makeID, generateUUID, makePrefixedID, makeTimestampID } from '@/utilities/id-generator';

describe('id-generator', () => {
    describe('makeID', () => {
        test('should generate a string ID', () => {
            const id = makeID();
            expect(typeof id).toBe('string');
        });

        test('should generate IDs of expected length', () => {
            const id = makeID();
            expect(id.length).toBeLessThanOrEqual(10);
            expect(id.length).toBeGreaterThan(0);
        });

        test('should generate unique IDs', () => {
            const ids = new Set();
            for (let i = 0; i < 100; i++) {
                ids.add(makeID());
            }
            // Should have generated mostly unique IDs
            expect(ids.size).toBeGreaterThan(95);
        });

        test('should generate alphanumeric IDs', () => {
            const id = makeID();
            expect(id).toMatch(/^[a-z0-9]+$/);
        });

        test('should not include special characters', () => {
            for (let i = 0; i < 50; i++) {
                const id = makeID();
                expect(id).not.toMatch(/[^a-z0-9]/);
            }
        });
    });

    describe('generateUUID', () => {
        test('should generate a string UUID', () => {
            const uuid = generateUUID();
            expect(typeof uuid).toBe('string');
        });

        test('should match UUID format', () => {
            const uuid = generateUUID();
            // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
            expect(uuid).toMatch(/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i);
        });

        test('should generate unique UUIDs', () => {
            const uuids = new Set();
            for (let i = 0; i < 100; i++) {
                uuids.add(generateUUID());
            }
            expect(uuids.size).toBe(100);
        });

        test('should always have 4 in the correct position', () => {
            for (let i = 0; i < 20; i++) {
                const uuid = generateUUID();
                expect(uuid.charAt(14)).toBe('4');
            }
        });

        test('should have correct variant bits', () => {
            for (let i = 0; i < 20; i++) {
                const uuid = generateUUID();
                const variantChar = uuid.charAt(19);
                expect(['8', '9', 'a', 'b']).toContain(variantChar.toLowerCase());
            }
        });
    });

    describe('makePrefixedID', () => {
        test('should generate ID with prefix', () => {
            const id = makePrefixedID('test');
            expect(id).toMatch(/^test_[a-z0-9]+$/);
        });

        test('should work with different prefixes', () => {
            const prefixes = ['user', 'item', 'resource', 'entity'];
            prefixes.forEach(prefix => {
                const id = makePrefixedID(prefix);
                expect(id).toMatch(new RegExp(`^${prefix}_[a-z0-9]+$`));
            });
        });

        test('should generate unique IDs with same prefix', () => {
            const ids = new Set();
            for (let i = 0; i < 50; i++) {
                ids.add(makePrefixedID('prefix'));
            }
            expect(ids.size).toBeGreaterThan(45);
        });

        test('should handle empty prefix', () => {
            const id = makePrefixedID('');
            expect(id).toMatch(/^_[a-z0-9]+$/);
        });

        test('should preserve prefix exactly', () => {
            const prefix = 'MyPrefix123';
            const id = makePrefixedID(prefix);
            expect(id.startsWith(prefix + '_')).toBe(true);
        });
    });

    describe('makeTimestampID', () => {
        test('should generate ID with timestamp', () => {
            const id = makeTimestampID();
            expect(id).toMatch(/^\d+_[a-z0-9]+$/);
        });

        test('should include current timestamp', () => {
            const before = Date.now();
            const id = makeTimestampID();
            const after = Date.now();
            
            const timestamp = parseInt(id.split('_')[0]);
            expect(timestamp).toBeGreaterThanOrEqual(before);
            expect(timestamp).toBeLessThanOrEqual(after);
        });

        test('should generate unique IDs even in quick succession', () => {
            const ids = [];
            for (let i = 0; i < 10; i++) {
                ids.push(makeTimestampID());
            }
            const uniqueIds = new Set(ids);
            expect(uniqueIds.size).toBe(ids.length);
        });

        test('should have both timestamp and random parts', () => {
            const id = makeTimestampID();
            const parts = id.split('_');
            expect(parts.length).toBe(2);
            expect(parts[0]).toMatch(/^\d+$/);
            expect(parts[1]).toMatch(/^[a-z0-9]+$/);
        });

        test('should generate sortable IDs by time', () => {
            const id1 = makeTimestampID();
            // Small delay to ensure different timestamp
            const id2 = makeTimestampID();
            
            // Timestamps should be in order (though might be same if very fast)
            const ts1 = parseInt(id1.split('_')[0]);
            const ts2 = parseInt(id2.split('_')[0]);
            expect(ts2).toBeGreaterThanOrEqual(ts1);
        });
    });
});
