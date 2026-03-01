import { useEffect, useState } from 'react'
import type { DashboardStats, Task } from '../types'

const STAT_CARDS = [
  { key: 'total_teams', label: 'Teams', icon: '⬡', color: 'text-nexus-accent-yellow' },
  { key: 'total_tasks', label: 'Tasks', icon: '◆', color: 'text-nexus-accent-blue' },
  { key: 'active_executions', label: 'Active', icon: '◉', color: 'text-nexus-accent-green' },
  { key: 'total_tokens', label: 'Tokens', icon: '⟐', color: 'text-nexus-accent-purple' },
] as const

const STATUS_BADGE: Record<string, string> = {
  pending: 'badge-pending',
  running: 'badge-running',
  completed: 'badge-completed',
  failed: 'badge-failed',
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/dashboard')
      .then(r => r.json())
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-nexus-accent-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-lg font-semibold text-white">Mission Control</h2>
        <p className="text-xs text-gray-500 font-mono mt-0.5">// harness engineering · multi-model orchestration</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STAT_CARDS.map(({ key, label, icon, color }) => (
          <div key={key} className="card">
            <div className="flex items-center justify-between mb-2">
              <span className={`text-lg ${color}`}>{icon}</span>
              <span className="text-[10px] text-gray-600 uppercase tracking-wider">{label}</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {key === 'total_tokens'
                ? ((stats?.[key] ?? 0) / 1000).toFixed(1) + 'k'
                : stats?.[key] ?? 0}
            </p>
          </div>
        ))}
      </div>

      {/* Cost & Models */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Total Cost</h3>
          <p className="text-3xl font-bold text-nexus-accent-green">
            ${(stats?.total_cost_usd ?? 0).toFixed(4)}
          </p>
        </div>
        <div className="card">
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Models Used</h3>
          <div className="flex flex-wrap gap-1.5">
            {(stats?.models_used ?? []).length > 0
              ? stats!.models_used.map(m => (
                  <span key={m} className="badge bg-nexus-accent-blue/10 text-nexus-accent-blue border border-nexus-accent-blue/20">
                    {m}
                  </span>
                ))
              : <span className="text-xs text-gray-600">No models used yet</span>
            }
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="card">
        <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-4">Recent Tasks</h3>
        {(stats?.recent_tasks ?? []).length > 0 ? (
          <div className="space-y-2">
            {stats!.recent_tasks.map((task: Task) => (
              <div key={task.id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-nexus-bg/50">
                <div className="flex items-center gap-3">
                  <span className={STATUS_BADGE[task.status] ?? 'badge'}>{task.status}</span>
                  <span className="text-sm text-gray-200">{task.name}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{task.steps?.length ?? 0} steps</span>
                  <span>{task.total_tokens.toLocaleString()} tokens</span>
                  <span className="font-mono">${task.total_cost_usd.toFixed(4)}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 text-sm">No tasks yet</p>
            <p className="text-gray-700 text-xs mt-1">Create a team and run your first task</p>
          </div>
        )}
      </div>

      {/* Architecture Reference */}
      <div className="card border-nexus-accent-yellow/20">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-nexus-accent-yellow text-sm">DEF</span>
          <h3 className="text-xs text-gray-400 uppercase tracking-wider">Harness Engineering</h3>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">
          Multi-model agent teams where each model has a specialized role.
          Opus orchestrates, Codex reviews, Sonnet builds, Qwen secures, Gemini designs.
          Structural constraints prevent errors — AGENTS.md, custom tools, verification loops.
        </p>
        <p className="text-[10px] text-gray-600 mt-2 font-mono italic">
          "Humans steer. Agents execute." — Mitchell Hashimoto, Feb 2026
        </p>
      </div>
    </div>
  )
}
