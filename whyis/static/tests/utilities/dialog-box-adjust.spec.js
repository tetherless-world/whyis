/**
 * @jest-environment jsdom
 */

import { processFloatList, resetProcessFloatList } from '../../js/whyis_vue/utilities/dialog-box-adjust';

describe('dialog-box-adjust utilities', () => {
  let intervalId;

  beforeEach(() => {
    // Clear any existing intervals
    if (intervalId) {
      clearInterval(intervalId);
    }
    // Clear document body
    document.body.innerHTML = '';
  });

  afterEach(() => {
    // Clean up intervals
    resetProcessFloatList();
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  });

  describe('processFloatList', () => {
    test('should return an interval ID', () => {
      intervalId = processFloatList();
      expect(typeof intervalId).toBe('number');
      expect(intervalId).toBeGreaterThan(0);
    });

    test('should set up an interval that runs periodically', (done) => {
      let callCount = 0;
      
      // Override setInterval to track calls
      const originalSetInterval = global.setInterval;
      global.setInterval = jest.fn((fn, delay) => {
        callCount++;
        expect(delay).toBe(40);
        return originalSetInterval(fn, delay);
      });

      intervalId = processFloatList();
      
      setTimeout(() => {
        expect(callCount).toBe(1);
        global.setInterval = originalSetInterval;
        done();
      }, 50);
    });

    test('should style dialog elements when they exist', (done) => {
      // Create a mock dialog element
      const dialogElement = document.createElement('div');
      dialogElement.className = 'md-menu-content-bottom-start';
      document.body.appendChild(dialogElement);

      intervalId = processFloatList();

      setTimeout(() => {
        const style = dialogElement.getAttribute('style');
        expect(style).toBeTruthy();
        expect(style).toContain('z-index:1000');
        expect(style).toContain('width: 410px');
        expect(style).toContain('max-width: 410px');
        expect(style).toContain('position: absolute');
        expect(style).toContain('transform:translateX(-50%)');
        done();
      }, 100);
    });

    test('should not throw error when no dialog elements exist', (done) => {
      expect(() => {
        intervalId = processFloatList();
      }).not.toThrow();

      setTimeout(() => {
        done();
      }, 100);
    });
  });

  describe('resetProcessFloatList', () => {
    test('should clear the interval', (done) => {
      intervalId = processFloatList();
      const id = intervalId;

      resetProcessFloatList();

      // Verify interval is cleared by checking it doesn't continue running
      const dialogElement = document.createElement('div');
      dialogElement.className = 'md-menu-content-bottom-start';
      document.body.appendChild(dialogElement);

      setTimeout(() => {
        // If interval was cleared, element shouldn't be styled
        const style = dialogElement.getAttribute('style');
        expect(style).toBeNull();
        done();
      }, 100);
    });

    test('should not throw error when called without active interval', () => {
      expect(() => {
        resetProcessFloatList();
      }).not.toThrow();
    });

    test('should return undefined', () => {
      intervalId = processFloatList();
      const result = resetProcessFloatList();
      expect(result).toBeUndefined();
    });
  });
});
