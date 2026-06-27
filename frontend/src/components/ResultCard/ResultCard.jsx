import { ExternalLinkIcon } from '../Icons/Icons'
import { formatScore, platformKey, capitalize } from '../../utils/format'
import styles from './ResultCard.module.css'

/**
 * @param {{ result: import('../../api/search').SearchResult }} props
 */
export function ResultCard({ result }) {
  const {
    title,
    url,
    description,
    platform,
    difficulty,
    tags,
    score,
  } = result

  const scorePct = formatScore(score)
  const pkey = platformKey(platform)

  return (
    <article className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.titleLink}
          >
            {title}
          </a>
        </h3>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.externalLink}
          aria-label={`Open "${title}" in new tab`}
          title="Open in new tab"
        >
          <ExternalLinkIcon width={16} height={16} />
        </a>
      </div>

      <div className={styles.meta}>
        <span
          className={`${styles.badge} ${styles.platform} ${styles[`platform_${pkey}`] || ''}`}
        >
          {capitalize(platform)}
        </span>
        {difficulty && (
          <span
            className={`${styles.badge} ${styles.difficulty} ${styles[`difficulty_${difficulty.toLowerCase()}`] || ''}`}
          >
            {capitalize(difficulty)}
          </span>
        )}
        {tags.slice(0, 4).map((tag) => (
          <span key={tag} className={styles.tag}>
            {tag}
          </span>
        ))}
      </div>

      <p className={styles.description}>{description}</p>

      <div className={styles.scoreRow}>
        <span className={styles.scoreLabel}>Relevance</span>
        <div
          className={styles.scoreBar}
          role="meter"
          aria-valuenow={scorePct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Relevance score ${scorePct}%`}
        >
          <div
            className={styles.scoreFill}
            style={{ width: `${scorePct}%` }}
          />
        </div>
        <span className={styles.scoreValue}>{scorePct}%</span>
      </div>
    </article>
  )
}
