import styles from './Skeleton.module.css'

export function SkeletonCard() {
  return (
    <div className={styles.card} aria-hidden="true">
      <div className={styles.header}>
        <div className={`${styles.line} ${styles.title}`} />
        <div className={`${styles.line} ${styles.icon}`} />
      </div>
      <div className={styles.badges}>
        <div className={`${styles.line} ${styles.badge}`} />
        <div className={`${styles.line} ${styles.badge}`} />
      </div>
      <div className={`${styles.line} ${styles.desc}`} />
      <div className={`${styles.line} ${styles.descShort}`} />
      <div className={styles.scoreRow}>
        <div className={`${styles.line} ${styles.scoreLabel}`} />
        <div className={`${styles.line} ${styles.scoreBar}`} />
        <div className={`${styles.line} ${styles.scoreValue}`} />
      </div>
    </div>
  )
}
