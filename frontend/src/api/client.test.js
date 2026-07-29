import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiClient, ApiError, _getBaseUrl } from './client'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

beforeEach(() => {
  vi.clearAllMocks()
})

describe('apiClient', () => {
  it('sends a request and returns parsed JSON on success', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' }),
    })
    const data = await apiClient('/api/health')
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/health',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    expect(data).toEqual({ status: 'ok' })
  })

  it('prepends the base URL from env', async () => {
    // Default env has empty VITE_API_BASE_URL → relative path
    expect(_getBaseUrl()).toBe('')
    mockFetch.mockResolvedValue({ ok: true, json: async () => ({}) })
    await apiClient('/api/search?q=x')
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/search?q=x',
      expect.any(Object)
    )
  })

  it('wraps network errors as ApiError with status 0', async () => {
    mockFetch.mockRejectedValue(new TypeError('Failed to fetch'))
    await expect(apiClient('/api/health')).rejects.toMatchObject({
      name: 'ApiError',
      status: 0,
    })
  })

  it('throws ApiError with status code on non-ok response', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({ detail: 'invalid' }),
    })
    await expect(apiClient('/api/search?q=')).rejects.toMatchObject({
      name: 'ApiError',
      status: 422,
    })
  })

  it('parses validation detail array into a message', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 422,
      json: async () => ({
        detail: [{ msg: 'field required' }, { msg: 'too long' }],
      }),
    })
    const err = await apiClient('/api/search?q=').catch((e) => e)
    expect(err).toBeInstanceOf(ApiError)
    expect(err.message).toContain('field required')
    expect(err.message).toContain('too long')
  })
})
