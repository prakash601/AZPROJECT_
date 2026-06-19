/**
 * Returns a debounced version of `fn` that waits `delay` ms after the last
 * call before invoking. Supports cancellation via `.cancel()` and an
 * immediate flush via `.flush()`.
 *
 * @template {(...args: any[]) => void} T
 * @param {T} fn
 * @param {number} delay - milliseconds
 * @returns {T & { cancel: () => void, flush: () => void }}
 */
export function debounce(fn, delay) {
  let timer = null
  let lastArgs = null

  const debounced = (...args) => {
    lastArgs = args
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      timer = null
      fn(...args)
    }, delay)
  }

  debounced.cancel = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  debounced.flush = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
      if (lastArgs) fn(...lastArgs)
    }
  }

  return debounced
}
