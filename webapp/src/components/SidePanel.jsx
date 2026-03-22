import { useEffect } from 'react'

export default function SidePanel({ isOpen, onClose, nodeId, targets }) {
  useEffect(() => {
    const handler = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  if (!isOpen) return null

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40 md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />
      <aside
        className="fixed bottom-0 left-0 right-0 md:right-0 md:left-auto md:top-0 md:bottom-0 md:w-96 z-50 bg-slate-800 border-t md:border-t-0 md:border-l border-slate-600 rounded-t-2xl md:rounded-none shadow-2xl flex flex-col max-h-[70vh] md:max-h-none"
        role="dialog"
        aria-label="Detalhes do versículo"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700 shrink-0">
          <h2 className="text-lg font-semibold text-amber-400 truncate pr-2">{nodeId}</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-700 text-gray-400 hover:text-white touch-manipulation"
            aria-label="Fechar"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto overscroll-contain px-4 py-3">
          <p className="text-sm text-gray-500 mb-2">Referências cruzadas ({targets.length})</p>
          <ul className="space-y-1.5">
            {targets.map((t) => (
              <li
                key={t}
                className="py-2 px-3 rounded-lg bg-slate-700/50 text-gray-200 text-sm"
              >
                {t}
              </li>
            ))}
            {targets.length === 0 && (
              <li className="text-gray-500 text-sm py-4">Nenhuma referência direta</li>
            )}
          </ul>
        </div>
      </aside>
    </>
  )
}
