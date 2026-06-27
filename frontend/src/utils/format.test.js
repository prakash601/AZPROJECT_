import { describe, it, expect } from 'vitest'
import { formatTime, formatScore, capitalize, platformKey, escapeHtml } from './format'

describe('formatTime', () => {
  it('returns <1 ms for sub-millisecond values', () => {
    expect(formatTime(0)).toBe('<1 ms')
    expect(formatTime(0.4)).toBe('<1 ms')
  })

  it('returns ms for values under 1000', () => {
    expect(formatTime(42)).toBe('42 ms')
    expect(formatTime(999)).toBe('999 ms')
  })

  it('returns seconds for 1000+', () => {
    expect(formatTime(1500)).toBe('1.50 s')
    expect(formatTime(1768)).toBe('1.77 s')
  })
})

describe('formatScore', () => {
  it('converts a 0–1 score to a percentage', () => {
    expect(formatScore(0.5)).toBe(50)
    expect(formatScore(0.8421)).toBe(84)
  })

  it('clamps to 0–100', () => {
    expect(formatScore(-0.5)).toBe(0)
    expect(formatScore(1.5)).toBe(100)
  })

  it('rounds to the nearest integer', () => {
    expect(formatScore(0.1885)).toBe(19)
    expect(formatScore(0.1518)).toBe(15)
  })
})

describe('capitalize', () => {
  it('capitalizes the first letter', () => {
    expect(capitalize('leetcode')).toBe('Leetcode')
  })

  it('handles empty strings', () => {
    expect(capitalize('')).toBe('')
    expect(capitalize(null)).toBe('')
  })
})

describe('platformKey', () => {
  it('returns known platforms lowercased', () => {
    expect(platformKey('LeetCode')).toBe('leetcode')
    expect(platformKey('CodeForces')).toBe('codeforces')
  })

  it('returns "default" for unknown platforms', () => {
    expect(platformKey('SPOJ')).toBe('default')
    expect(platformKey('')).toBe('default')
  })
})

describe('escapeHtml', () => {
  it('escapes HTML special characters', () => {
    expect(escapeHtml('<script>alert("x")</script>')).toBe(
      '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'
    )
  })

  it('handles null/undefined', () => {
    expect(escapeHtml(null)).toBe('')
    expect(escapeHtml(undefined)).toBe('')
  })
})
