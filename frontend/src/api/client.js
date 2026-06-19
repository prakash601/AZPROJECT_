/**
 * Fetch wrapper for the API.
 * - Reads base URL from env (empty in dev → relative paths + Vite proxy)
 * - Normalizes errors into a consistent shape
 * - Returns parsed JSON
 */

export function _getBaseUrl() {
  // Read lazily so tests can override import.meta.env after import.
  return import.meta.env.VITE_API_BASE_URL || ''
}

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

/**
 * @param {string} path - path beginning with /api
 * @param {RequestInit} [init]
 * @returns {Promise<any>}
 */
export async function apiClient(path, init) {
  let response
  try {
    response = await fetch(`${_getBaseUrl()}${path}`, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...init?.headers,
      },
    })
  } catch (err) {
    // Network error / server unreachable
    throw new ApiError(
      'Cannot reach the server. Please check your connection.',
      0,
      err
    )
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    let details = null
    try {
      const body = await response.json()
      if (body?.detail) {
        details = body.detail
        message = Array.isArray(body.detail)
          ? body.detail.map((d) => d.msg).join(', ')
          : String(body.detail)
      }
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(message, response.status, details)
  }

  return response.json()
}
