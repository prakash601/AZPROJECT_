import { describe, it, expect, vi } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useAutocomplete } from './useAutocomplete'

// Mock the API so we control timing without real network calls
vi.mock('../api/search', () => ({
  getAutocomplete: vi.fn(),
}))

import { getAutocomplete } from '../api/search'

describe('useAutocomplete', () => {
  it('starts empty and not loading', () => {
    const { result } = renderHook(() => useAutocomplete(150))
    expect(result.current.suggestions).toEqual([])
    expect(result.current.loading).toBe(false)
  })

  it('does not fetch for empty/whitespace prefix', () => {
    const { result } = renderHook(() => useAutocomplete(150))
    act(() => {
      result.current.fetchSuggestions('   ')
    })
    expect(getAutocomplete).not.toHaveBeenCalled()
    expect(result.current.suggestions).toEqual([])
  })

  it('clears suggestions and stops loading', async () => {
    getAutocomplete.mockResolvedValue({
      prefix: 'two',
      suggestions: [
        { id: 1, title: 'Two Sum', url: 'u', platform: 'leetcode' },
      ],
    })
    const { result } = renderHook(() => useAutocomplete(150))
    act(() => {
      result.current.fetchSuggestions('two')
    })
    act(() => {
      result.current.clear()
    })
    expect(result.current.suggestions).toEqual([])
    expect(result.current.loading).toBe(false)
  })
})
