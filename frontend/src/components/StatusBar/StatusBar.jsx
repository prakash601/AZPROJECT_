import { formatTime } from '../../utils/format'
import styles from './StatusBar.module.css'

/**
 * @param {{
 *   data: import('../../api/search').SearchResponse|null,
 *   didYouMean: string|null,
 *   onDidYouMean: (q: string) => void,
 * }} props
 */
export function StatusBar({ data, didYouMean, onDidYouMean }) {
  if (!data) return null
  const { query, execution_time_ms, count } = data

  return (
    <div className={styles.bar}>
      <p className={styles.summary}>
        <span className={styles.count}>{count}</span>{' '}
        {count === 1 ? 'result' : 'results'} for{' '}
        <span className={styles.query}>&ldquo;{query}&rdquo;</span>
        <span className={styles.time}>· {formatTime(execution_time_ms)}</span>
      </p>
      {didYouMean && didYouMean !== query && (
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
