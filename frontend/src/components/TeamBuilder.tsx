import { useEffect, useState } from 'react'
import type { Team, AgentConfig } from '../types'

const ROLE_COLORS: Record<string, string> = {
  orchestrator: '#F59E0B',
  backend: '#3B82F6',
  frontend: '#10B981',
  security: '#EC4899',
  researcher: '#F97316',
  designer: '#8B5CF6',
  reviewer: '#06B6D4',
  tester: '#6366F1',
}

const PRESETS = {
  model: [
    { label: 'Claude Opus 4.6', value: 'claude-opus-4-6', provider: 'anthropic' },
    { label: 'GPT-5.3-Codex', value: 'gpt-5.3-codex', provider: 'openai' },
    { label: 'Claude Sonnet 4.6', value: 'claude-sonnet-4-6-20250514', provider: 'anthropic' },
    { label: 'Qwen 3.5', value: 'openrouter/qwen/qwen3-coder', provider: 'alibaba' },
    { label: 'Gemini 3.1 Pro', value: 'gemini-3.1-pro', provider: 'google' },
    { label: 'DeepSeek V3', value: 'swarm/deepseek-v3', provider: 'deepseek' },
  ],
  role: ['orchestrator', 'backend', 'frontend', 'security', 'researcher', 'designer', 'reviewer', 'tester'],
}

export function TeamBuilder() {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  const loadTeams = () => {
    fetch('/api/teams')
      .then(r => r.json())
      .then(d => setTeams(d.teams ?? []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(loadTeams, [])

  const createHarnessPreset = async () => {
    setCreating(true)
    try {
      await fetch('/api/teams/preset/harness', { method: 'POST' })
      loadTeams()
    } finally {
      setCreating(false)
    }
  }

  const deleteTeam = async (id: string) => {
    await fetch(`/api/teams/${id}`, { method: 'DELETE' })
    loadTeams()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-nexus-accent-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Agent Teams</h2>
          <p className="text-xs text-gray-500 font-mono mt-0.5">// compose multi-model teams with specialized roles</p>
        </div>
        <button
          onClick={createHarnessPreset}
          disabled={creating}
          className="btn-primary flex items-center gap-2"
        >
          {creating ? (
            <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <span>⚡</span>
          )}
          Create Harness Team
        </button>
      </div>

      {teams.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-4xl mb-4">⬡</p>
          <p className="text-gray-400 text-sm">No teams configured</p>
          <p className="text-gray-600 text-xs mt-1 mb-4">
            Create a Harness Engineering team to get started
          </p>
          <button onClick={createHarnessPreset} className="btn-primary mx-auto">
            ⚡ Quick Start: Harness Team
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {teams.map(team => (
            <div key={team.id} className="card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-white">{team.name}</h3>
                  <p className="text-xs text-gray-500 mt-0.5">{team.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-600 font-mono">{team.id}</span>
                  <button onClick={() => deleteTeam(team.id)} className="text-gray-600 hover:text-red-400 text-xs">
                    ✕
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {team.agents.map((agent: AgentConfig) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function AgentCard({ agent }: { agent: AgentConfig }) {
  const borderColor = ROLE_COLORS[agent.role] ?? '#6B7280'

  return (
    <div
      className="bg-nexus-bg/60 rounded-lg p-3 border transition-all hover:bg-nexus-bg/80"
      style={{ borderColor: `${borderColor}33`, borderWidth: 1 }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: borderColor }} />
        <span className="text-[10px] text-gray-500 uppercase tracking-wider">{agent.role}</span>
      </div>
      <h4 className="text-sm font-medium text-white mb-1">{agent.name}</h4>
      <p className="text-[11px] text-gray-400 mb-2 line-clamp-2">{agent.description}</p>
      <div className="flex items-center justify-between">
        <span className="text-[10px] text-gray-600 font-mono truncate max-w-[60%]">{agent.model}</span>
        <span
          className="badge text-[10px]"
          style={{ backgroundColor: `${borderColor}15`, color: borderColor, borderColor: `${borderColor}30` }}
        >
          {agent.provider}
        </span>
      </div>
    </div>
  )
}
