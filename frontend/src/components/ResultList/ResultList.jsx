import { ResultCard } from '../ResultCard/ResultCard'
import { SkeletonCard } from '../Skeleton/Skeleton'
import { AlertIcon, SearchEmptyIcon } from '../Icons/Icons'
import styles from './ResultList.module.css'

/**
 * @param {{
 *   status: 'idle'|'loading'|'success'|'error',
 *   data: import('../../api/search').SearchResponse|null,
 *   error: string|null,
 *   onRetry: () => void,
 *   didYouMean: string|null,
 *   onDidYouMean: (q: string) => void,
 * }} props
 */
export function ResultList({ status, data, error, onRetry, didYouMean, onDidYouMean }) {
  if (status === 'idle') {
    return (
      <div className={styles.placeholder}>
        <SearchEmptyIcon width={48} height={48} className={styles.placeholderIcon} />
        <h2 className={styles.placeholderTitle}>Search for a problem</h2>
        <p className={styles.placeholderText}>
          Type a query above — semantic, keyword, and fuzzy search combined via
          Reciprocal Rank Fusion.
        </p>
      </div>
    )
  }

  if (status === 'loading') {
    return (
      <div className={styles.list} aria-busy="true" aria-live="polite">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className={styles.placeholder} role="alert">
        <AlertIcon width={48} height={48} className={styles.errorIcon} />
        <h2 className={styles.placeholderTitle}>Something went wrong</h2>
        <p className={styles.placeholderText}>{error}</p>
        <button type="button" className={styles.retry} onClick={onRetry}>
          Try again
        </button>
      </div>
    )
  }

  // success
  const results = data?.results ?? []
  if (results.length === 0) {
    return (
      <div className={styles.placeholder}>
        <SearchEmptyIcon width={48} height={48} className={styles.placeholderIcon} />
        <h2 className={styles.placeholderTitle}>No results found</h2>
        <p className={styles.placeholderText}>
          We couldn't find any problems matching{' '}
          <strong>{data?.query}</strong>. Try different keywords.
        </p>
        {didYouMean && (
          <button
            type="button"
            className={styles.didYouMean}
            onClick={() => onDidYouMean(didYouMean)}
          >
            Did you mean <strong>{didYouMean}</strong>?
          </button>
        )}
      </div>
    )
  }

  return (
    <div className={styles.list} aria-live="polite">
      {results.map((result) => (
        <ResultCard key={result.id} result={result} />
      ))}
    </div>
  )
}
