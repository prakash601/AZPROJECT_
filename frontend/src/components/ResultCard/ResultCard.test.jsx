import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ResultCard } from './ResultCard'

const baseResult = {
  id: 1,
  platform: 'leetcode',
  title: 'Two Sum',
  url: 'https://leetcode.com/problems/two-sum',
  description:
    'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
  difficulty: 'Easy',
  tags: ['array', 'hash-table'],
  score: 0.8421,
}

describe('ResultCard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the title as a link', () => {
    render(<ResultCard result={baseResult} />)
    const link = screen.getByRole('link', { name: 'Two Sum' })
    expect(link).toHaveAttribute('href', 'https://leetcode.com/problems/two-sum')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('renders the platform badge', () => {
    render(<ResultCard result={baseResult} />)
    expect(screen.getByText('Leetcode')).toBeInTheDocument()
  })

  it('renders the difficulty badge when present', () => {
    render(<ResultCard result={baseResult} />)
    expect(screen.getByText('Easy')).toBeInTheDocument()
  })

  it('does not render the difficulty badge when null', () => {
    const r = { ...baseResult, difficulty: null }
    render(<ResultCard result={r} />)
    // "Easy" should not appear since difficulty is null
    // The platform "Leetcode" will still be there.
    const badges = screen.getAllByText(/Leetcode|Easy|Medium|Hard/)
    expect(badges).toHaveLength(1)
    expect(badges[0]).toHaveTextContent('Leetcode')
  })

  it('renders up to 4 tags', () => {
    const r = {
      ...baseResult,
      tags: ['array', 'hash-table', 'sorting', 'two-pointers', 'extra'],
    }
    render(<ResultCard result={r} />)
    expect(screen.getByText('array')).toBeInTheDocument()
    expect(screen.getByText('hash-table')).toBeInTheDocument()
    expect(screen.getByText('sorting')).toBeInTheDocument()
    expect(screen.getByText('two-pointers')).toBeInTheDocument()
    expect(screen.queryByText('extra')).not.toBeInTheDocument()
  })

  it('renders the description', () => {
    render(<ResultCard result={baseResult} />)
    expect(
      screen.getByText(/Given an array of integers/)
    ).toBeInTheDocument()
  })

  it('renders the relevance meter with the score percentage', () => {
    render(<ResultCard result={baseResult} />)
    // 0.8421 -> 84%
    const meter = screen.getByRole('meter')
    expect(meter).toHaveAttribute('aria-valuenow', '84')
    expect(screen.getByText('84%')).toBeInTheDocument()
  })

  it('renders an external-link button with an accessible label', () => {
    render(<ResultCard result={baseResult} />)
    expect(
      screen.getByRole('link', {
        name: /Open "Two Sum" in new tab/i,
      })
    ).toBeInTheDocument()
  })

  it('opens links in a new tab with rel attributes', async () => {
    const user = userEvent.setup()
    render(<ResultCard result={baseResult} />)
    const external = screen.getByRole('link', {
      name: /Open "Two Sum" in new tab/i,
    })
    expect(external).toHaveAttribute('target', '_blank')
    expect(external).toHaveAttribute('rel', 'noopener noreferrer')
    // Not actually clicking — jsdom doesn't navigate; verifying attributes only.
    await user.tab()
  })
})
