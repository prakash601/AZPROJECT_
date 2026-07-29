import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Autocomplete } from './Autocomplete'

const suggestions = [
  {
    id: 1,
    title: 'Two Sum',
    url: 'https://leetcode.com/problems/two-sum',
    platform: 'leetcode',
  },
  {
    id: 2,
    title: 'Two TVs',
    url: 'https://codeforces.com/problemset/problem/845/C',
    platform: 'codeforces',
  },
  {
    id: 3,
    title: 'Two-gram',
    url: 'https://codeforces.com/problemset/problem/977/B',
    platform: 'codeforces',
  },
]

describe('Autocomplete', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when not visible', () => {
    const { container } = render(
      <Autocomplete
        suggestions={suggestions}
        loading={false}
        activeIndex={-1}
        visible={false}
        query="two"
        onSelect={() => {}}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders the listbox and options when visible', () => {
    render(
      <Autocomplete
        suggestions={suggestions}
        loading={false}
        activeIndex={-1}
        visible={true}
        query="two"
        onSelect={() => {}}
      />
    )
    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getAllByRole('option')).toHaveLength(3)
    expect(screen.getByText('Two Sum')).toBeInTheDocument()
  })

  it('marks the active option as aria-selected', () => {
    render(
      <Autocomplete
        suggestions={suggestions}
        loading={false}
        activeIndex={1}
        visible={true}
        query="two"
        onSelect={() => {}}
      />
    )
    const options = screen.getAllByRole('option')
    expect(options[0]).toHaveAttribute('aria-selected', 'false')
    expect(options[1]).toHaveAttribute('aria-selected', 'true')
    expect(options[2]).toHaveAttribute('aria-selected', 'false')
  })

  it('shows a loading message when loading with no suggestions', () => {
    render(
      <Autocomplete
        suggestions={[]}
        loading={true}
        activeIndex={-1}
        visible={true}
        query="two"
        onSelect={() => {}}
      />
    )
    expect(screen.getByText(/Loading suggestions/)).toBeInTheDocument()
  })

  it('shows an empty state when there are no matches', () => {
    render(
      <Autocomplete
        suggestions={[]}
        loading={false}
        activeIndex={-1}
        visible={true}
        query="xyz"
        onSelect={() => {}}
      />
    )
    expect(screen.getByText(/No matches for/)).toBeInTheDocument()
  })

  it('calls onSelect when an option is clicked (mousedown)', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    render(
      <Autocomplete
        suggestions={suggestions}
        loading={false}
        activeIndex={-1}
        visible={true}
        query="two"
        onSelect={onSelect}
      />
    )
    const options = screen.getAllByRole('option')
    // mousedown is what the component listens for (to fire before blur)
    await user.pointer([
      { target: options[1], keys: '[MouseLeft>]' },
      { keys: '[/MouseLeft]' },
    ])
    expect(onSelect).toHaveBeenCalledWith(suggestions[1])
  })
})
