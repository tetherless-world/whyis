
export default function debounce (func, millis) {
  let timeout
  return function (...args) {
    const functionCall = () => func.apply(this, args)
    clearTimeout(timeout)
    timeout = setTimeout(functionCall, millis)
  }
}
