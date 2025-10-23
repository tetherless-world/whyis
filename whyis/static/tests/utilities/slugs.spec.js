/**
 * @jest-environment jsdom
 */

import Slug from '../../js/whyis_vue/modules/slugs';

describe('slugs module', () => {
  test('should return string as-is for simple alphanumeric input', () => {
    expect(Slug('Hello World')).toBe('Hello World');
    expect(Slug('Test123')).toBe('Test123');
  });

  test('should trim leading and trailing whitespace', () => {
    expect(Slug('  Hello World  ')).toBe('Hello World');
    expect(Slug('\t\nTest\t\n')).toBe('Test');
  });

  test('should replace accented characters with ASCII equivalents', () => {
    expect(Slug('Café')).toBe('Cafe');
    expect(Slug('François')).toBe('Francois');
    expect(Slug('Müller')).toBe('Muller');
    expect(Slug('naïve')).toBe('naive');
  });

  test('should handle Greek letters', () => {
    expect(Slug('α β γ')).toBe('a b g');
    expect(Slug('Ω')).toBe('W'); // Omega maps to W in the slugs module
  });

  test('should handle Cyrillic characters', () => {
    expect(Slug('Привет')).toBe('Privet');
  });

  test('should collapse multiple spaces', () => {
    expect(Slug('Hello    World')).toBe('Hello World');
    expect(Slug('Too   Many    Spaces')).toBe('Too Many Spaces');
  });

  test('should remove invalid characters', () => {
    expect(Slug('Test™')).toBe('Test');
    expect(Slug('Hello®World')).toBe('HelloWorld');
  });

  test('should keep allowed special characters', () => {
    expect(Slug('Hello & World')).toBe('Hello & World');
    expect(Slug('Test-Name')).toBe('Test-Name');
    expect(Slug('email@example.com')).toBe('email@example.com');
  });

  test('should handle numbers with special formatting', () => {
    expect(Slug('Test¹²³')).toBe('Test123');
    expect(Slug('H₂O')).toBe('H2O');
  });

  test('should handle empty strings', () => {
    expect(Slug('')).toBe('');
  });

  test('should convert to string if not already', () => {
    expect(Slug(123)).toBe('123');
    expect(Slug(null)).toBe('null');
  });

  test('should remove leading/trailing dashes after processing', () => {
    expect(Slug('-Test-')).toBe('Test');
    expect(Slug('---Multiple---')).toBe('Multiple');
  });

  test('should collapse multiple consecutive dashes', () => {
    expect(Slug('Test---Name')).toBe('Test-Name');
  });

  test('should handle copyright symbol', () => {
    expect(Slug('Copyright © 2024')).toBe('Copyright (c) 2024');
  });

  test('should handle mixed case and special characters', () => {
    const input = 'François Müller™ & Associates®';
    const result = Slug(input);
    expect(result).toBe('Francois Muller & Associates');
  });

  test('should handle complex Unicode strings', () => {
    expect(Slug('こんにちは')).toBe('');
    expect(Slug('Hello 世界')).toBe('Hello '); // Trailing space from removed character
  });
});
