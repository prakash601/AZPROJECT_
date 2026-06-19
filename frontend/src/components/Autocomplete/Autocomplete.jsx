import { useEffect, useRef } from 'react'
import { SearchIcon } from '../Icons/Icons'
import { capitalize, platformKey } from '../../utils/format'
import styles from './Autocomplete.module.css'

/**
 * @param {{
 *   suggestions: import('../../api/search').AutocompleteSuggestion[],
 *   loading: boolean,
 *   activeIndex: number,
 *   visible: boolean,
 *   query: string,
 *   onSelect: (s: import('../../api/search').AutocompleteSuggestion) => void,
 * }} props
 */
export function Autocomplete({
  suggestions,
  loading,
  activeIndex,
  visible,
  query,
  onSelect,
}) {
  const listRef = useRef(null)

  // Scroll the active item into view as the user navigates with the keyboard
  useEffect(() => {
    if (!visible || activeIndex < 0) return
    const el = listRef.current?.querySelector(
      `[data-index="${activeIndex}"]`
    )
    el?.scrollIntoView({ block: 'nearest' })
  }, [activeIndex, visible])

  if (!visible) return null

  const hasSuggestions = suggestions.length > 0

  return (
    <div
      className={styles.dropdown}
      role="listbox"
      aria-label="Search suggestions"
      ref={listRef}
    >
      {loading && !hasSuggestions && (
        <div className={styles.loading} aria-live="polite">
          Loading suggestions…
        </div>
      )}

      {!loading && !hasSuggestions && (
        <div className={styles.empty}>No matches for &ldquo;{query}&rdquo;</div>
      )}

      {hasSuggestions && (
        <ul className={styles.list}>
          {suggestions.map((s, i) => {
            const pkey = platformKey(s.platform)
            return (
              <li
                key={s.id}
                data-index={i}
                role="option"
                aria-selected={i === activeIndex}
                className={`${styles.item} ${i === activeIndex ? styles.active : ''}`}
                onMouseDown={(e) => {
                  // prevent blur before click
                  e.preventDefault()
                  onSelect(s)
                }}
                onMouseEnter={() => {
                  /* parent tracks index via onMouseMove if needed */
                }}
              >
                <SearchIcon
                  width={14}
                  height={14}
                  className={styles.itemIcon}
                />
                <span className={styles.itemTitle}>{s.title}</span>
                <span
                  className={`${styles.itemPlatform} ${styles[`platform_${pkey}`] || ''}`}
                >
                  {capitalize(s.platform)}
                </span>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
