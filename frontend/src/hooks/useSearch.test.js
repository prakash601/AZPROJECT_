import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSearch } from './useSearch'

// Mock the API module
vi.mock('../api/search', () => ({
  searchProblems: vi.fn(),
}))

import { searchProblems } from '../api/search'

describe('useSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts in idle state', () => {
    const { result } = renderHook(() => useSearch())
    expect(result.current.status).toBe('idle')
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('stays idle for empty/whitespace queries without calling the API', async () => {
    const { result } = renderHook(() => useSearch())
    await act(async () => {
      await result.current.search('   ')
    })
    expect(searchProblems).not.toHaveBeenCalled()
    expect(result.current.status).toBe('idle')
  })

  it('transitions to loading then success', async () => {
    const mockResponse = {
      query: 'two sum',
      corrected_query: null,
      execution_time_ms: 42,
      count: 1,
      results: [
        {
          id: 1,
          platform: 'leetcode',
          title: 'Two Sum',
          url: 'https://example.com',
          description: 'desc',
          difficulty: 'Easy',
          tags: ['array'],
          score: 0.9,
        },
      ],
    }
    searchProblems.mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useSearch())

    let searchPromise
    act(() => {
      searchPromise = result.current.search('two sum')
    })
    expect(result.current.status).toBe('loading')

    await act(async () => {
      await searchPromise
    })
    expect(result.current.status).toBe('success')
    expect(result.current.data).toEqual(mockResponse)
    expect(result.current.error).toBeNull()
  })

  it('transitions to error on failure', async () => {
    searchProblems.mockRejectedValue(new Error('Network down'))

    const { result } = renderHook(() => useSearch())

    await act(async () => {
      await result.current.search('fail')
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Network down')
  })

  it('reset returns to idle and clears state', async () => {
    searchProblems.mockResolvedValue({
      query: 'x',
      corrected_query: null,
      execution_time_ms: 1,
      count: 0,
      results: [],
    })
    const { result } = renderHook(() => useSearch())
    await act(async () => {
      await result.current.search('x')
    })
    expect(result.current.status).toBe('success')

    act(() => {
      result.current.reset()
    })
    expect(result.current.status).toBe('idle')
    expect(result.current.data).toBeNull()
    expect(result.current.error).toBeNull()
  })
})
