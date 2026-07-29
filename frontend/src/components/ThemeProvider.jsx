import { ThemeContext } from '../context/ThemeContext'
import { useThemeState } from '../hooks/useTheme'

export function ThemeProvider({ children }) {
  const value = useThemeState()
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
