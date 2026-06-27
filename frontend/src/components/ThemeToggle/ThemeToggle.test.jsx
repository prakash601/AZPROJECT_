import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeContext } from '../../context/ThemeContext'
import { ThemeToggle } from './ThemeToggle'

function renderWithTheme(theme, toggleTheme = vi.fn()) {
  return render(
    <ThemeContext.Provider
      value={{ theme, setTheme: vi.fn(), toggleTheme }}
    >
      <ThemeToggle />
    </ThemeContext.Provider>
  )
}

describe('ThemeToggle', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows a button to switch to light mode when in dark mode', () => {
    renderWithTheme('dark')
    expect(
      screen.getByRole('button', { name: /switch to light mode/i })
    ).toBeInTheDocument()
  })

  it('shows a button to switch to dark mode when in light mode', () => {
    renderWithTheme('light')
    expect(
      screen.getByRole('button', { name: /switch to dark mode/i })
    ).toBeInTheDocument()
  })

  it('calls toggleTheme when the button is clicked', () => {
    const toggleTheme = vi.fn()
    renderWithTheme('light', toggleTheme)
    fireEvent.click(screen.getByRole('button'))
    expect(toggleTheme).toHaveBeenCalledTimes(1)
  })
})
