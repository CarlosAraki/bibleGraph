import { useState, useEffect, useCallback, useRef } from 'react'
import { SigmaContainer, useLoadGraph, useSigma, useRegisterEvents, useCamera } from '@react-sigma/core'
import { LayoutForceAtlas2Control } from '@react-sigma/layout-forceatlas2'
import Graph from 'graphology'
import '@react-sigma/core/lib/style.css'
import SearchBar from './components/SearchBar'
import SidePanel from './components/SidePanel'
import LoadingScreen from './components/LoadingScreen'
import ViewTabs from './components/ViewTabs'

const DATA_BASE = '/data'

function LoadGraph({ graphData, onGraphReady }) {
  const loadGraph = useLoadGraph()
  useEffect(() => {
    if (!graphData) return
    const graph = Graph.from(graphData)
    loadGraph(graph)
    onGraphReady?.(graph)
  }, [graphData, loadGraph, onGraphReady])
  return null
}

function GraphController({ selectedNode, onSelectNode, originalAttrsRef }) {
  const sigma = useSigma()
  const { gotoNode } = useCamera()
  const registerEvents = useRegisterEvents()

  const resetHighlight = useCallback(() => {
    if (!sigma || !originalAttrsRef.current) return
    const graph = sigma.getGraph()
    graph.forEachNode((n) => {
      const orig = originalAttrsRef.current[n]
      if (orig) {
        graph.mergeNodeAttributes(n, { color: orig.color, size: orig.size })
      }
    })
    sigma.refresh()
  }, [sigma, originalAttrsRef])

  useEffect(() => {
    if (!selectedNode || !sigma) {
      resetHighlight()
      return
    }
    const graph = sigma.getGraph()
    if (!graph.hasNode(selectedNode)) return

    const neighbors = new Set()
    graph.forEachNeighbor(selectedNode, (n) => neighbors.add(n))
    graph.forEachInNeighbor(selectedNode, (n) => neighbors.add(n))

    gotoNode(selectedNode, { duration: 500 })

    const HIGHLIGHT = '#fbbf24'
    const DIM = '#1e293b'
    const DIM_SIZE = 0.4

    graph.forEachNode((n, attrs) => {
      const orig = originalAttrsRef.current?.[n]
      const baseSize = orig?.size ?? attrs.size ?? 5
      if (n === selectedNode || neighbors.has(n)) {
        graph.mergeNodeAttributes(n, { color: HIGHLIGHT, size: Math.max(baseSize * 2, 12) })
      } else {
        graph.mergeNodeAttributes(n, { color: DIM, size: Math.max(baseSize * DIM_SIZE, 1) })
      }
    })
    sigma.refresh()

    return () => resetHighlight()
  }, [selectedNode, sigma, gotoNode, resetHighlight])

  useEffect(() => {
    if (!registerEvents || !sigma) return
    registerEvents({
      clickNode: ({ node }) => onSelectNode(node),
      clickStage: () => onSelectNode(null),
    })
  }, [registerEvents, sigma, onSelectNode])

  return null
}

function AppContent() {
  const [view, setView] = useState('top500')
  const [graphData, setGraphData] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingMsg, setLoadingMsg] = useState('A processar as escrituras...')
  const [verses, setVerses] = useState([])
  const originalAttrsRef = useRef({})

  const graphUrl = view === 'full' ? `${DATA_BASE}/graph_full.json` : `${DATA_BASE}/graph_top500.json`

  useEffect(() => {
    setSelectedNode(null)
    setLoading(true)
    setLoadingMsg(view === 'full' ? 'Carregando grafo completo (~25MB)...' : 'A processar as escrituras...')
    fetch(graphUrl)
      .then((r) => r.json())
      .then((data) => {
        setGraphData(data)
        setLoading(false)
      })
      .catch(() => {
        setLoadingMsg('Erro ao carregar dados.')
        setLoading(false)
      })
  }, [graphUrl, view])

  useEffect(() => {
    fetch(`${DATA_BASE}/verses_autocomplete.json`)
      .then((r) => r.json())
      .then(setVerses)
      .catch(() => setVerses([]))
  }, [])

  const handleGraphReady = useCallback((graph) => {
    const attrs = {}
    graph.forEachNode((n, a) => {
      attrs[n] = { color: a.color, size: a.size }
    })
    originalAttrsRef.current = attrs
  }, [])

  const targets = selectedNode && graphData
    ? (() => {
        const g = Graph.from(graphData)
        const out = []
        g.forEachOutNeighbor(selectedNode, (n) => out.push(n))
        return out
      })()
    : []

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0f172a] text-gray-200 overflow-hidden">
      {loading && <LoadingScreen message={loadingMsg} />}

      <header className="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-[#1e293b] border-b border-slate-700/50 gap-2">
        <h1 className="text-base sm:text-lg font-semibold truncate">Referências Cruzadas da Bíblia</h1>
        <ViewTabs view={view} onChange={setView} />
      </header>

      <div className="flex-1 relative flex min-h-0">
        <SearchBar verses={verses} onSelect={setSelectedNode} />

        <div className="flex-1 min-w-0 relative">
          <SigmaContainer
            style={{ height: '100%', width: '100%' }}
            settings={{
              defaultNodeColor: '#6366f1',
              defaultNodeType: 'circle',
              defaultEdgeColor: '#475569',
              defaultEdgeType: 'arrow',
              labelDensity: 0.07,
              labelGridCellSize: 60,
              labelRenderedSizeThreshold: 8,
              zIndex: true,
              enableEdgeWheelEvents: false,
              enableEdgeEvents: false,
            }}
          >
            <LoadGraph graphData={graphData} onGraphReady={handleGraphReady} />
            <GraphController
              selectedNode={selectedNode}
              onSelectNode={setSelectedNode}
              originalAttrsRef={originalAttrsRef}
            />
            <LayoutForceAtlas2Control
              settings={{ iterations: 50, linLogMode: true }}
              autoRunFor={3000}
              className="absolute bottom-4 left-4 !bg-slate-800/90 !border-slate-600"
            />
          </SigmaContainer>
        </div>
      </div>

      <SidePanel
        isOpen={!!selectedNode}
        onClose={() => setSelectedNode(null)}
        nodeId={selectedNode}
        targets={targets}
      />
    </div>
  )
}

export default function App() {
  return <AppContent />
}
