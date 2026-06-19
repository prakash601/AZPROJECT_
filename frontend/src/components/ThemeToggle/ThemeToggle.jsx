import { useTheme } from '../../context/ThemeContext'
import { SunIcon, MoonIcon } from '../Icons/Icons'
import styles from './ThemeToggle.module.css'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'
  const Icon = isDark ? SunIcon : MoonIcon

  return (
    <button
      type="button"
      className={styles.toggle}
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <Icon className={styles.icon} width={18} height={18} />
    </button>
  )
}
