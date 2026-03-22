export default function LoadingScreen({ message = 'A processar as escrituras...' }) {
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#0f172a]">
      <div className="w-12 h-12 border-4 border-amber-400/30 border-t-amber-400 rounded-full animate-spin" />
      <p className="mt-4 text-gray-400 text-sm">{message}</p>
    </div>
  )
}
