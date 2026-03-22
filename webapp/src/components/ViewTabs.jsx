export default function ViewTabs({ view, onChange }) {
  return (
    <div className="flex rounded-lg overflow-hidden bg-slate-700/50 p-0.5">
      <button
        onClick={() => onChange('top500')}
        className={`px-3 py-1.5 text-sm font-medium transition-colors touch-manipulation ${
          view === 'top500'
            ? 'bg-amber-500/80 text-slate-900'
            : 'text-gray-300 hover:bg-slate-600/50'
        }`}
      >
        Top 500
      </button>
      <button
        onClick={() => onChange('full')}
        className={`px-3 py-1.5 text-sm font-medium transition-colors touch-manipulation ${
          view === 'full'
            ? 'bg-amber-500/80 text-slate-900'
            : 'text-gray-300 hover:bg-slate-600/50'
        }`}
      >
        Visão Global
      </button>
    </div>
  )
}
