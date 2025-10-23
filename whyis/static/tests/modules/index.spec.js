/**
 * @jest-environment jsdom
 */

describe('modules index', () => {
  test('should export EventServices', () => {
    const modules = require('../../js/whyis_vue/modules/index');
    expect(modules.EventServices).toBeDefined();
  });

  test('should export Slug', () => {
    const modules = require('../../js/whyis_vue/modules/index');
    expect(modules.Slug).toBeDefined();
    expect(typeof modules.Slug).toBe('function');
  });

  test('should have exactly two exports', () => {
    const modules = require('../../js/whyis_vue/modules/index');
    const exports = Object.keys(modules);
    expect(exports.length).toBe(2);
    expect(exports).toContain('EventServices');
    expect(exports).toContain('Slug');
  });

  test('EventServices should be an object', () => {
    const { EventServices } = require('../../js/whyis_vue/modules/index');
    expect(typeof EventServices).toBe('object');
  });

  test('Slug should be a function', () => {
    const { Slug } = require('../../js/whyis_vue/modules/index');
    expect(typeof Slug).toBe('function');
  });
});
