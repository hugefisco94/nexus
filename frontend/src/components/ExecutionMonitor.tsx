import { useEffect, useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import type { Execution, Task, WsMessage } from '../types'

const PHASE_STYLES: Record<string, { color: string; label: string }> = {
  queued: { color: '#6B7280', label: 'QUEUED' },
  thinking: { color: '#F59E0B', label: 'THINKING' },
  executing: { color: '#3B82F6', label: 'EXECUTING' },
  reviewing: { color: '#8B5CF6', label: 'REVIEWING' },
  done: { color: '#10B981', label: 'DONE' },
  error: { color: '#EF4444', label: 'ERROR' },
}

export function ExecutionMonitor() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [executions, setExecutions] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)
  const { messages } = useWebSocket()

  useEffect(() => {
    Promise.all([
      fetch('/api/tasks').then(r => r.json()),
      fetch('/api/executions').then(r => r.json()),
    ])
      .then(([t, e]) => {
        setTasks(t.tasks ?? [])
        setExecutions(e.executions ?? [])
      })
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
      <div>
        <h2 className="text-lg font-semibold text-white">Execution Monitor</h2>
        <p className="text-xs text-gray-500 font-mono mt-0.5">
          // self-cloning · parallel execution · real-time
        </p>
      </div>

      {/* Live Feed */}
      {messages.length > 0 && (
        <div className="card border-nexus-accent-green/20">
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="pulse-dot bg-green-400" />
            Live Feed
          </h3>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {messages.slice(0, 20).map((msg: WsMessage, i: number) => (
              <div key={i} className="text-xs font-mono text-gray-400 py-0.5">
                <span className="text-gray-600">[{msg.type}]</span>{' '}
                {msg.agent_name && <span className="text-nexus-accent-blue">{msg.agent_name}</span>}
                {msg.phase && <span className="text-nexus-accent-yellow ml-2">{msg.phase}</span>}
                {msg.output_preview && (
                  <span className="text-gray-500 ml-2 truncate inline-block max-w-md">
                    {msg.output_preview}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Grid — self-cloning visualization */}
      {executions.length > 0 ? (
        <div>
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">
            Agent Clones · Parallel Execution
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {executions.map(exec => {
              const phase = PHASE_STYLES[exec.phase] ?? PHASE_STYLES.queued
              return (
                <div
                  key={exec.id}
                  className="bg-nexus-surface rounded-lg p-4 border transition-all"
                  style={{ borderColor: `${phase.color}33` }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] text-gray-500 uppercase tracking-wider font-mono">
                      CLONE · {exec.id.slice(0, 4)}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ backgroundColor: phase.color }}
                      />
                      <span className="text-[10px] font-mono" style={{ color: phase.color }}>
                        {phase.label}
                      </span>
                    </div>
                  </div>
                  <h4 className="text-sm font-medium text-white mb-1">{exec.agent_name}</h4>
                  <p className="text-[10px] text-gray-500 font-mono mb-2 truncate">{exec.model}</p>
                  {exec.output_preview && (
                    <p className="text-xs text-gray-400 line-clamp-2 mt-2 bg-nexus-bg/50 rounded p-2">
                      {exec.output_preview}
                    </p>
                  )}
                  <div className="flex items-center justify-between mt-2 text-[10px] text-gray-600">
                    <span>{(exec.tokens_in + exec.tokens_out).toLocaleString()} tokens</span>
                    <span>${exec.cost_usd.toFixed(4)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        <div className="card text-center py-16">
          <p className="text-4xl mb-4">◉</p>
          <p className="text-gray-400 text-sm">No active executions</p>
          <p className="text-gray-600 text-xs mt-1">Execute a task to see agents working in parallel</p>
        </div>
      )}

      {/* Task List */}
      {tasks.length > 0 && (
        <div className="card">
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Task History</h3>
          <div className="space-y-2">
            {tasks.map(task => (
              <TaskRow key={task.id} task={task} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function TaskRow({ task }: { task: Task }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-nexus-bg/50 rounded-lg">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between py-2.5 px-3 text-left"
      >
        <div className="flex items-center gap-3">
          <span className={`badge-${task.status}`}>{task.status}</span>
          <span className="text-sm text-gray-200">{task.name}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>{task.steps.length} steps</span>
          <span className="font-mono">{task.total_tokens.toLocaleString()} tok</span>
          <span className="text-gray-600">{expanded ? '▲' : '▼'}</span>
        </div>
      </button>
      {expanded && (
        <div className="px-3 pb-3 space-y-1">
          {task.steps.map(step => (
            <div key={step.id} className="flex items-center gap-2 py-1 text-xs">
              <span className={`w-1.5 h-1.5 rounded-full ${
                step.status === 'completed' ? 'bg-green-400' :
                step.status === 'running' ? 'bg-blue-400 animate-pulse' :
                step.status === 'failed' ? 'bg-red-400' : 'bg-gray-600'
              }`} />
              <span className="text-gray-300">{step.name}</span>
              {step.duration_ms > 0 && (
                <span className="text-gray-600 font-mono">{(step.duration_ms / 1000).toFixed(1)}s</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
