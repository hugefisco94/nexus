export type ModelProvider = 'anthropic' | 'openai' | 'google' | 'alibaba' | 'moonshot' | 'deepseek' | 'local'
export type AgentRole = 'orchestrator' | 'backend' | 'frontend' | 'security' | 'researcher' | 'designer' | 'reviewer' | 'tester'
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type ExecutionPhase = 'queued' | 'thinking' | 'executing' | 'reviewing' | 'done' | 'error'

export interface AgentConfig {
  id: string
  name: string
  model: string
  provider: ModelProvider
  role: AgentRole
  description: string
  reasoning_effort: string
  max_tokens: number
  temperature: number
  color: string
}

export interface Team {
  id: string
  name: string
  description: string
  agents: AgentConfig[]
  created_at: string
  updated_at: string
}

export interface TaskStep {
  id: string
  name: string
  prompt: string
  assigned_agent_id: string
  depends_on: string[]
  status: TaskStatus
  result: string | null
  tokens_used: number
  cost_usd: number
  started_at: string | null
  completed_at: string | null
  duration_ms: number
}

export interface Task {
  id: string
  team_id: string
  name: string
  description: string
  steps: TaskStep[]
  status: TaskStatus
  created_at: string
  started_at: string | null
  completed_at: string | null
  total_tokens: number
  total_cost_usd: number
}

export interface Execution {
  id: string
  task_id: string
  step_id: string
  agent_id: string
  agent_name: string
  model: string
  phase: ExecutionPhase
  output_preview: string
  tokens_in: number
  tokens_out: number
  cost_usd: number
  started_at: string | null
  completed_at: string | null
  error: string | null
}

export interface DashboardStats {
  total_teams: number
  total_tasks: number
  active_executions: number
  total_tokens: number
  total_cost_usd: number
  models_used: string[]
  recent_tasks: Task[]
}

export interface WsMessage {
  type: string
  task_id?: string
  step_id?: string
  agent_name?: string
  model?: string
  phase?: string
  error?: string
  tokens?: number
  duration_ms?: number
  output_preview?: string
  status?: string
  total_tokens?: number
  total_cost_usd?: number
}
