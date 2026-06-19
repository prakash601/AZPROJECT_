import { ThemeToggle } from '../ThemeToggle/ThemeToggle'
import { GithubIcon } from '../Icons/Icons'
import styles from './Header.module.css'

export function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <a href="/" className={styles.brand} aria-label="Problem Finder — home">
          <span className={styles.logo} aria-hidden="true">
            {'{ }'}
          </span>
          <span className={styles.name}>Problem Finder</span>
        </a>

        <nav className={styles.nav} aria-label="Primary">
          <a
            href="https://github.com/prakash601/AZPROJECT_"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.navLink}
            title="Source code"
          >
            <GithubIcon width={18} height={18} />
            <span>Source</span>
          </a>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  )
}
