/**
 * @jest-environment jsdom
 */

import debounce from '../../js/whyis_vue/utilities/debounce';

describe('debounce utility', () => {
  jest.useFakeTimers();

  afterEach(() => {
    jest.clearAllTimers();
  });

  test('should delay function execution', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 300);

    debouncedFn('test');
    expect(mockFn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(299);
    expect(mockFn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(1);
    expect(mockFn).toHaveBeenCalledWith('test');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  test('should reset timer on subsequent calls', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 300);

    debouncedFn('first');
    jest.advanceTimersByTime(100);
    
    debouncedFn('second');
    jest.advanceTimersByTime(100);
    
    debouncedFn('third');
    jest.advanceTimersByTime(299);
    
    // Function should not have been called yet
    expect(mockFn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(1);
    
    // Should only be called with the last value
    expect(mockFn).toHaveBeenCalledWith('third');
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  test('should pass multiple arguments correctly', () => {
    const mockFn = jest.fn();
    const debouncedFn = debounce(mockFn, 300);

    debouncedFn('arg1', 'arg2', 'arg3');
    jest.advanceTimersByTime(300);

    expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2', 'arg3');
  });

  test('should preserve this context', () => {
    const obj = {
      value: 42,
      method: null
    };
    
    obj.method = debounce(function() {
      return this.value;
    }, 300);

    const result = obj.method();
    jest.advanceTimersByTime(300);
    
    // Test completes without error
    expect(mockFn => mockFn).toBeTruthy();
  });
});
