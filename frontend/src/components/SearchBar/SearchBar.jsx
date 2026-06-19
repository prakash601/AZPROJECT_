import { useCallback, useEffect, useRef, useState } from 'react'
import { SearchIcon } from '../Icons/Icons'
import { Autocomplete } from '../Autocomplete/Autocomplete'
import { useAutocomplete } from '../../hooks/useAutocomplete'
import styles from './SearchBar.module.css'

/**
 * @param {{
 *   value: string,
 *   onValueChange: (v: string) => void,
 *   onSubmit: (v: string) => void,
 * }} props
 */
export function SearchBar({ value, onValueChange, onSubmit }) {
  const [focused, setFocused] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const inputRef = useRef(null)
  const { suggestions, loading, fetchSuggestions, clear } = useAutocomplete()

  const showDropdown = focused && value.trim().length > 0

  // Clamp activeIndex when suggestions shrink or dropdown hides (derived, not effect)
  const safeActiveIndex =
    showDropdown && activeIndex >= 0 && suggestions.length > 0
      ? activeIndex % suggestions.length
      : -1

  const handleSubmit = useCallback(
    (q) => {
      clear()
      setFocused(false)
      setActiveIndex(-1)
      onSubmit(q)
    },
    [clear, onSubmit]
  )

  const handleInputChange = (e) => {
    const v = e.target.value
    onValueChange(v)
    setActiveIndex(-1)
    fetchSuggestions(v)
  }

  const selectSuggestion = (s) => {
    onValueChange(s.title)
    handleSubmit(s.title)
  }

  const handleKeyDown = (e) => {
    if (!showDropdown || suggestions.length === 0) {
      if (e.key === 'Enter') {
        e.preventDefault()
        handleSubmit(value)
      }
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setActiveIndex((i) => (i + 1) % suggestions.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setActiveIndex((i) => (i - 1 + suggestions.length) % suggestions.length)
        break
      case 'Enter':
        e.preventDefault()
        if (safeActiveIndex >= 0 && safeActiveIndex < suggestions.length) {
          selectSuggestion(suggestions[safeActiveIndex])
        } else {
          handleSubmit(value)
        }
        break
      case 'Escape':
        e.preventDefault()
        setFocused(false)
        setActiveIndex(-1)
        clear()
        break
      case 'Tab':
        setFocused(false)
        clear()
        break
      default:
        break
    }
  }

  // Global "/" shortcut to focus the search
  useEffect(() => {
    const onKey = (e) => {
      if (
        e.key === '/' &&
        document.activeElement?.tagName !== 'INPUT' &&
        document.activeElement?.tagName !== 'TEXTAREA'
      ) {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className={styles.wrapper}>
      <form
        className={styles.form}
        onSubmit={(e) => {
          e.preventDefault()
          handleSubmit(value)
        }}
        role="search"
      >
        <div className={styles.inputWrap}>
          <SearchIcon
            className={styles.searchIcon}
            width={18}
            height={18}
            aria-hidden="true"
          />
          <input
            ref={inputRef}
            type="text"
            className={styles.input}
            placeholder="Search coding problems…  (press / to focus)"
            value={value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setTimeout(() => setFocused(false), 120)}
            aria-label="Search coding problems"
            aria-expanded={showDropdown}
            aria-controls="autocomplete-listbox"
            aria-autocomplete="list"
            aria-activedescendant={
              activeIndex >= 0 ? `suggestion-${activeIndex}` : undefined
            }
            autoComplete="off"
            spellCheck="false"
          />
        </div>
        <button type="submit" className={styles.submit}>
          Search
        </button>
      </form>

      <Autocomplete
        suggestions={suggestions}
        loading={loading}
        activeIndex={safeActiveIndex}
        visible={showDropdown}
        query={value}
        onSelect={selectSuggestion}
      />
    </div>
  )
}
