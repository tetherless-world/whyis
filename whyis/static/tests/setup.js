// Mock for global window objects used in Whyis Vue components
global.window = Object.create(window);
global.window.NODE_URI = 'http://example.org/test';
global.window.ROOT_URL = 'http://localhost/';
global.window.LOD_PREFIX = 'http://example.org/';
global.window.USER = { id: 'test-user' };

// Mock navigator if needed
Object.defineProperty(window, 'navigator', {
  value: {
    userAgent: 'jest'
  },
  writable: true
});
