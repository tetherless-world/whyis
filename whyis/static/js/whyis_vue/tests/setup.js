/**
 * Test setup configuration for Vitest
 * Sets up global mocks and utilities for Vue component testing
 */

import { vi } from 'vitest';
import Vue from 'vue';
import * as VueMaterial from 'vue-material';

// Configure Vue with Material Design components (same as main.js)
Vue.use(VueMaterial.default);

// Mock global variables that are typically set by the templates
global.LOD_PREFIX = 'http://example.org/';
global.BASE_RATE = 0.5;
global.USER = { uri: 'http://example.org/user/test', admin: false, name: 'Test User', email: 'test@example.com' };
global.NAVIGATION = { showAddKnowledgeMenu: false, showUploadDialog: false };
global.NODE_URI = 'http://example.org/resource/test';
global.ATTRIBUTES = {};
global.SUMMARY = {};
global.DESCRIPTION = [];
global.NODE = { '@id': 'http://example.org/resource/test' };
global.ROOT_URL = 'http://example.org/';
global.LINKS = { registerNav: '/register', changePasswordNav: '/change-password' };
global.CONFIGS = { mongoBackup: false, speedDialIcon: false };

// Mock axios for HTTP requests
global.axios = {
  get: vi.fn(() => Promise.resolve({ data: {} })),
  post: vi.fn(() => Promise.resolve({ data: {} })),
  put: vi.fn(() => Promise.resolve({ data: {} })),
  delete: vi.fn(() => Promise.resolve({ data: {} })),
  defaults: { headers: { common: {} } }
};

// Mock browser APIs
global.window = Object.create(window);

// Mock location more carefully
const mockLocation = {
  href: 'http://example.org/',
  origin: 'http://example.org',
  reload: vi.fn()
};

Object.defineProperty(global.window, 'location', {
  value: mockLocation,
  writable: true,
  configurable: true
});

// Also mock encodeURIComponent
global.window.encodeURIComponent = global.encodeURIComponent || vi.fn((str) => str);

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn()
};