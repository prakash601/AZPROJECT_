/**
 * Search & autocomplete API functions.
 * Typed JSDoc mirrors the FastAPI Pydantic models in main.py.
 */

import { apiClient } from './client'

/**
 * @typedef {Object} SearchResult
 * @property {number} id
 * @property {string} platform
 * @property {string} title
 * @property {string} url
 * @property {string} description
 * @property {string|null} difficulty
 * @property {string[]} tags
 * @property {number} score
 */

/**
 * @typedef {Object} SearchResponse
 * @property {string} query
 * @property {string|null} corrected_query
 * @property {number} execution_time_ms
 * @property {number} count
 * @property {SearchResult[]} results
 */

/**
 * @typedef {Object} AutocompleteSuggestion
 * @property {number} id
 * @property {string} title
 * @property {string} url
 * @property {string} platform
 */

/**
 * @typedef {Object} AutocompleteResponse
 * @property {string} prefix
 * @property {AutocompleteSuggestion[]} suggestions
 */

/**
 * Search coding problems.
 * @param {string} query
 * @param {{ limit?: number, offset?: number, signal?: AbortSignal }} [opts]
 * @returns {Promise<SearchResponse>}
 */
export function searchProblems(query, opts = {}) {
  const { limit = 30, offset = 0, signal } = opts
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
    offset: String(offset),
  })
  return apiClient(`/api/search?${params}`, { signal })
}

/**
 * Autocomplete a prefix.
 * @param {string} prefix
 * @param {{ limit?: number, signal?: AbortSignal }} [opts]
 * @returns {Promise<AutocompleteResponse>}
 */
export function getAutocomplete(prefix, opts = {}) {
  const { limit = 10, signal } = opts
  const params = new URLSearchParams({ prefix, limit: String(limit) })
  return apiClient(`/api/autocomplete?${params}`, { signal })
}
