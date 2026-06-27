import { useCallback, useRef, useState } from 'react'
import { searchProblems } from '../api/search'

/**
 * @typedef {'idle'|'loading'|'success'|'error'} SearchStatus
 */

/**
 * Search hook — drives an idle/loading/success/error state machine.
 * Supports cancellation (in-flight requests are aborted if a new one starts)
 * so the UI never shows stale results.
 *
 * @returns {{
 *   status: SearchStatus,
 *   data: import('../api/search').SearchResponse|null,
 *   error: string|null,
 *   search: (query: string, opts?: {limit?:number, offset?:number}) => Promise<void>,
 *   reset: () => void,
 * }}
 */
export function useSearch() {
  const [status, setStatus] = useState('idle')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  const search = useCallback(async (query, opts = {}) => {
    const trimmed = query.trim()
    if (!trimmed) {
      setStatus('idle')
      setData(null)
      setError(null)
      return
    }

    // Cancel any in-flight request
    if (abortRef.current) abortRef.current.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setStatus('loading')
    setError(null)

    try {
      const res = await searchProblems(trimmed, {
        limit: opts.limit ?? 30,
        offset: opts.offset ?? 0,
        signal: controller.signal,
      })
      setData(res)
      setStatus('success')
    } catch (err) {
      if (err.name === 'AbortError' || err.name === 'TypeError') {
        // Aborted by a newer request — do not clobber the new state
        return
      }
      setError(err.message || 'Something went wrong')
      setStatus('error')
    } finally {
      if (abortRef.current === controller) abortRef.current = null
    }
  }, [])

  const reset = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    setStatus('idle')
    setData(null)
    setError(null)
  }, [])

  return { status, data, error, search, reset }
}
