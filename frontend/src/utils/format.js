/**
 * Formatting helpers for display.
 */

/**
 * Escape a string for safe insertion into HTML.
 * @param {string} str
 * @returns {string}
 */
export function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

/**
 * Format an execution time in ms into a human string.
 * @param {number} ms
 * @returns {string}
 */
export function formatTime(ms) {
  if (ms < 1) return '<1 ms'
  if (ms < 1000) return `${ms} ms`
  return `${(ms / 1000).toFixed(2)} s`
}

/**
 * Normalize a relevance score (0–1-ish) to a percentage 0–100.
 * @param {number} score
 * @returns {number}
 */
export function formatScore(score) {
  const pct = Math.round(score * 100)
  return Math.max(0, Math.min(100, pct))
}

/**
 * Capitalize the first letter.
 * @param {string} s
 * @returns {string}
 */
export function capitalize(s) {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/**
 * Normalize a platform name for CSS class + display.
 * @param {string} platform
 * @returns {string}
 */
export function platformKey(platform) {
  const p = (platform || '').toLowerCase().trim()
  const known = [
    'leetcode',
    'codeforces',
    'codechef',
    'hackerrank',
    'hackerearth',
    'atcoder',
  ]
  return known.includes(p) ? p : 'default'
}
