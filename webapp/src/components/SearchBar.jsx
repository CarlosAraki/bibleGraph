import { useState, useRef, useEffect } from 'react'

const MAX_RESULTS = 15

export default function SearchBar({ verses, onSelect, graphData }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [open, setOpen] = useState(false)
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef(null)
  const listRef = useRef(null)

  const filtered = query.trim()
    ? verses.filter((v) =>
        v.toLowerCase().includes(query.toLowerCase())
      ).slice(0, MAX_RESULTS)
    : []

  useEffect(() => {
    setResults(filtered)
    setSelectedIdx(0)
  }, [query, verses])

  useEffect(() => {
    if (selectedIdx >= 0 && listRef.current) {
      const el = listRef.current.children[selectedIdx]
      el?.scrollIntoView({ block: 'nearest' })
    }
  }, [selectedIdx])

  const handleSelect = (verse) => {
    onSelect(verse)
    setQuery('')
    setOpen(false)
  }

  const handleKeyDown = (e) => {
    if (!open || results.length === 0) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIdx((i) => Math.min(i + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIdx((i) => Math.max(i - 1, 0))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      const v = results[selectedIdx]
      if (v) handleSelect(v)
    } else if (e.key === 'Escape') {
      setOpen(false)
      inputRef.current?.blur()
    }
  }

  return (
    <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 w-[90%] max-w-md">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setOpen(true)
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Pesquisar versículo (ex: João 3:16)"
          className="w-full px-4 py-3 pr-10 rounded-xl bg-slate-800/95 border border-slate-600 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-amber-400/50 focus:border-amber-400"
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">⌘K</span>
      </div>
      {open && results.length > 0 && (
        <ul
          ref={listRef}
          className="absolute top-full left-0 right-0 mt-1 max-h-60 overflow-auto rounded-xl bg-slate-800/98 border border-slate-600 shadow-xl"
        >
          {results.map((v, i) => (
            <li
              key={v}
              onClick={() => handleSelect(v)}
              className={`px-4 py-2.5 cursor-pointer text-sm ${
                i === selectedIdx ? 'bg-amber-500/20 text-amber-300' : 'text-gray-300 hover:bg-slate-700'
              }`}
            >
              {v}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
