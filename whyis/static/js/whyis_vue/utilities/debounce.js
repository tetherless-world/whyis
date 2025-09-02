
/**
 * Creates a debounced function that delays invoking func until after millis milliseconds
 * have elapsed since the last time the debounced function was invoked.
 * 
 * @param {Function} func - The function to debounce
 * @param {number} millis - The number of milliseconds to delay
 * @returns {Function} The debounced function
 * @example
 * const debouncedSearch = debounce(searchFunction, 300);
 * debouncedSearch('query'); // Will only execute after 300ms of no additional calls
 */
export default function debounce (func, millis) {
  let timeout
  return function (...args) {
    const functionCall = () => func.apply(this, args)
    clearTimeout(timeout)
    timeout = setTimeout(functionCall, millis)
  }
}
