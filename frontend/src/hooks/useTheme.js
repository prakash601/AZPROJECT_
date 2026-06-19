import { useCallback, useEffect, useState } from 'react'

const STORAGE_KEY = 'pf-theme'

/**
 * Theme hook: reads system preference on first visit, persists choice to
 * localStorage, applies [data-theme] attribute on <html>.
 *
 * @returns {{ theme: 'light'|'dark', setTheme: (t:'light'|'dark')=>void, toggleTheme: ()=>void }}
 */
export function useThemeState() {
  const [theme, setThemeState] = useState(() => {
    if (typeof window === 'undefined') return 'light'
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
    // Fall back to OS preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const setTheme = useCallback((t) => setThemeState(t), [])

  const toggleTheme = useCallback(
    () => setThemeState((t) => (t === 'dark' ? 'light' : 'dark')),
    []
  )

  return { theme, setTheme, toggleTheme }
}
