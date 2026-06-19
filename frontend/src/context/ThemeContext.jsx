import { createContext, useContext } from 'react'

/**
 * @typedef {'light' | 'dark'} Theme
 * @typedef {(theme: Theme) => void} SetTheme
 */

export const ThemeContext = createContext({
  /** @type {Theme} */
  theme: 'light',
  /** @type {SetTheme} */
  setTheme: () => {},
  /** @type {() => void} */
  toggleTheme: () => {},
})

export const useTheme = () => useContext(ThemeContext)
