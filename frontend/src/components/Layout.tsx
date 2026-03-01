import { type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useWebSocket } from '../hooks/useWebSocket'

const NAV = [
  { path: '/', label: 'Dashboard', icon: '◆' },
  { path: '/teams', label: 'Teams', icon: '⬡' },
  { path: '/monitor', label: 'Monitor', icon: '◉' },
  { path: '/results', label: 'Results', icon: '◧' },
]

export function Layout({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()
  const { connected } = useWebSocket()

  return (
    <div className="min-h-screen bg-nexus-bg">
      {/* Header */}
      <header className="border-b border-nexus-border bg-nexus-bg/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-nexus-accent-blue to-nexus-accent-purple flex items-center justify-center text-white font-bold text-sm">
              N
            </div>
            <div>
              <h1 className="text-sm font-semibold text-white tracking-wide">NEXUS</h1>
              <p className="text-[10px] text-gray-500 font-mono tracking-widest">AI AGENT MISSION CONTROL</p>
            </div>
          </div>

          <nav className="flex items-center gap-1">
            {NAV.map(({ path, label, icon }) => (
              <Link
                key={path}
                to={path}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  pathname === path
                    ? 'bg-nexus-accent-blue/15 text-nexus-accent-blue border border-nexus-accent-blue/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-nexus-surface'
                }`}
              >
                <span className="mr-1.5">{icon}</span>
                {label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-1.5 text-xs ${connected ? 'text-green-400' : 'text-red-400'}`}>
              <span className={`pulse-dot ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
              {connected ? 'Live' : 'Offline'}
            </div>
            <span className="text-[10px] text-gray-600 font-mono">v0.1.0</span>
          </div>
        </div>
      </header>

      <div className="glow-line" />

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {children}
      </main>
    </div>
  )
}
