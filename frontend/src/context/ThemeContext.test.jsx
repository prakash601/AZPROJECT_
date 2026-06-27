import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render } from '@testing-library/react'
import { ThemeContext, useTheme } from './ThemeContext'

describe('ThemeContext + useTheme', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exposes theme, setTheme, toggleTheme to consumers', () => {
    const value = { theme: 'dark', setTheme: vi.fn(), toggleTheme: vi.fn() }
    let consumed
    function Consumer() {
      consumed = useTheme()
      return null
    }
    render(
      <ThemeContext.Provider value={value}>
        <Consumer />
      </ThemeContext.Provider>
    )
    expect(consumed).toEqual(value)
    expect(consumed.theme).toBe('dark')
    expect(typeof consumed.setTheme).toBe('function')
    expect(typeof consumed.toggleTheme).toBe('function')
  })

  it('uses the default context value when no provider is present', () => {
    let consumed
    function Consumer() {
      consumed = useTheme()
      return null
    }
    render(<Consumer />)
    expect(consumed.theme).toBe('light')
    expect(typeof consumed.toggleTheme).toBe('function')
    // The default no-op toggle should not throw
    expect(() => consumed.toggleTheme()).not.toThrow()
  })
})
