import { useEffect, useState } from 'react'
import type { Task, TaskStep } from '../types'

export function ResultsViewer() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [selected, setSelected] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/tasks')
      .then(r => r.json())
      .then(d => {
        const completed = (d.tasks ?? []).filter((t: Task) => t.status === 'completed' || t.status === 'failed')
        setTasks(completed)
        if (completed.length > 0) setSelected(completed[0])
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
        <h2 className="text-lg font-semibold text-white">Results</h2>
        <p className="text-xs text-gray-500 font-mono mt-0.5">// aggregated outputs · step-by-step results</p>
      </div>

      {tasks.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-4xl mb-4">◧</p>
          <p className="text-gray-400 text-sm">No completed tasks</p>
          <p className="text-gray-600 text-xs mt-1">Execute tasks to see their results here</p>
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-4">
          {/* Task Sidebar */}
          <div className="col-span-3">
            <div className="card space-y-1">
              {tasks.map(task => (
                <button
                  key={task.id}
                  onClick={() => setSelected(task)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                    selected?.id === task.id
                      ? 'bg-nexus-accent-blue/10 text-nexus-accent-blue'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-nexus-bg/50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      task.status === 'completed' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className="truncate">{task.name}</span>
                  </div>
                  <div className="text-[10px] text-gray-600 mt-0.5 font-mono">
                    {task.steps.length} steps · {task.total_tokens.toLocaleString()} tok
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Results Detail */}
          <div className="col-span-9">
            {selected ? (
              <div className="space-y-4">
                {/* Summary */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-white">{selected.name}</h3>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className={`badge-${selected.status}`}>{selected.status}</span>
                      <span className="font-mono">${selected.total_cost_usd.toFixed(4)}</span>
                    </div>
                  </div>
                  {selected.description && (
                    <p className="text-xs text-gray-400 mb-3">{selected.description}</p>
                  )}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-nexus-bg/50 rounded-lg p-2.5 text-center">
                      <p className="text-lg font-bold text-white">{selected.steps.length}</p>
                      <p className="text-[10px] text-gray-600">Steps</p>
                    </div>
                    <div className="bg-nexus-bg/50 rounded-lg p-2.5 text-center">
                      <p className="text-lg font-bold text-white">{selected.total_tokens.toLocaleString()}</p>
                      <p className="text-[10px] text-gray-600">Tokens</p>
                    </div>
                    <div className="bg-nexus-bg/50 rounded-lg p-2.5 text-center">
                      <p className="text-lg font-bold text-nexus-accent-green">${selected.total_cost_usd.toFixed(4)}</p>
                      <p className="text-[10px] text-gray-600">Cost</p>
                    </div>
                  </div>
                </div>

                {/* Step Results */}
                {selected.steps.map((step: TaskStep, idx: number) => (
                  <div key={step.id} className="card">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-gray-600 font-mono">STEP {idx + 1}</span>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          step.status === 'completed' ? 'bg-green-400' : 'bg-red-400'
                        }`} />
                        <h4 className="text-sm font-medium text-white">{step.name}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-gray-600">
                        {step.duration_ms > 0 && <span className="font-mono">{(step.duration_ms / 1000).toFixed(1)}s</span>}
                        <span>{step.tokens_used.toLocaleString()} tok</span>
                      </div>
                    </div>
                    {step.result ? (
                      <pre className="bg-nexus-bg/60 rounded-lg p-3 text-xs text-gray-300 font-mono whitespace-pre-wrap overflow-x-auto max-h-64 overflow-y-auto">
                        {step.result}
                      </pre>
                    ) : (
                      <p className="text-xs text-gray-600 italic">No output</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <p className="text-gray-500 text-sm">Select a task to view results</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
