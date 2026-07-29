import { useCallback, useEffect, useState } from 'react'
import { Header } from './components/Header/Header'
import { Footer } from './components/Footer/Footer'
import { SearchBar } from './components/SearchBar/SearchBar'
import { ResultList } from './components/ResultList/ResultList'
import { StatusBar } from './components/StatusBar/StatusBar'
import { ThemeProvider } from './components/ThemeProvider'
import { useSearch } from './hooks/useSearch'
import styles from './App.module.css'

function getQueryParam() {
  const params = new URLSearchParams(window.location.search)
  return params.get('q') || ''
}

export default function App() {
  const { status, data, error, search, reset } = useSearch()
  const [query, setQuery] = useState(getQueryParam)

  // Sync query to URL ?q= so searches are shareable & back-button works
  const syncUrl = useCallback((q) => {
    const url = new URL(window.location.href)
    if (q.trim()) url.searchParams.set('q', q)
    else url.searchParams.delete('q')
    window.history.replaceState({}, '', url)
  }, [])

  // Handle browser back/forward
  useEffect(() => {
    const onPop = () => {
      const q = getQueryParam()
      setQuery(q)
      if (q.trim()) search(q)
      else reset()
    }
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [search, reset])

  // Fire initial search if ?q= present on load
  useEffect(() => {
    const q = getQueryParam()
    if (q.trim()) search(q)
  }, [search])

  const handleSubmit = useCallback(
    (q) => {
      setQuery(q)
      syncUrl(q)
      if (q.trim()) search(q)
      else reset()
    },
    [search, reset, syncUrl]
  )

  const handleDidYouMean = useCallback(
    (q) => {
      setQuery(q)
      syncUrl(q)
      search(q)
    },
    [search, syncUrl]
  )

  const handleRetry = useCallback(() => {
    if (query.trim()) search(query)
  }, [query, search])

  return (
    <ThemeProvider>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <Header />
      <main id="main" className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.title}>Find your next problem</h1>
          <p className={styles.subtitle}>
            Semantic + keyword + fuzzy search across coding platforms
          </p>
        </div>

        <SearchBar
          value={query}
          onValueChange={setQuery}
          onSubmit={handleSubmit}
        />

        <div className={styles.results}>
          {status === 'success' && data && (
            <StatusBar
              data={data}
              didYouMean={data.corrected_query}
              onDidYouMean={handleDidYouMean}
            />
          )}
          <ResultList
            status={status}
            data={data}
            error={error}
            onRetry={handleRetry}
            didYouMean={data?.corrected_query ?? null}
            onDidYouMean={handleDidYouMean}
          />
        </div>
      </main>
      <Footer />
    </ThemeProvider>
  )
}
