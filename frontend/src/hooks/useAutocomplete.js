import { useCallback, useEffect, useRef, useState } from 'react'
import { getAutocomplete } from '../api/search'
import { debounce } from '../utils/debounce'

/**
 * Autocomplete hook — debounces prefix input (150ms), cancels stale
 * requests, and exposes suggestions + loading state.
 *
 * @param {number} [delay=150]
 * @returns {{
 *   suggestions: import('../api/search').AutocompleteSuggestion[],
 *   loading: boolean,
 *   fetchSuggestions: (prefix: string) => void,
 *   clear: () => void,
 * }}
 */
export function useAutocomplete(delay = 150) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const abortRef = useRef(null)
  const debouncedRef = useRef(null)

  // Build the debounced fetcher in an effect so no ref is captured during render.
  useEffect(() => {
    const run = async (prefix) => {
      if (abortRef.current) abortRef.current.abort()
      const controller = new AbortController()
      abortRef.current = controller

      setLoading(true)
      try {
        const res = await getAutocomplete(prefix, { signal: controller.signal })
        setSuggestions(res.suggestions || [])
      } catch (err) {
        if (err.name === 'AbortError') return
        setSuggestions([])
      } finally {
        if (abortRef.current === controller) {
          abortRef.current = null
          setLoading(false)
        }
      }
    }
    debouncedRef.current = debounce(run, delay)
    return () => debouncedRef.current?.cancel()
  }, [delay])

  const fetchSuggestions = useCallback((prefix) => {
    const p = prefix.trim()
    if (!p) {
      if (abortRef.current) abortRef.current.abort()
      setSuggestions([])
      setLoading(false)
      return
    }
    debouncedRef.current?.(p)
  }, [])

  const clear = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    debouncedRef.current?.cancel()
    setSuggestions([])
    setLoading(false)
  }, [])

  return { suggestions, loading, fetchSuggestions, clear }
}
