import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './components/Dashboard'
import { TeamBuilder } from './components/TeamBuilder'
import { ExecutionMonitor } from './components/ExecutionMonitor'
import { ResultsViewer } from './components/ResultsViewer'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/teams" element={<TeamBuilder />} />
        <Route path="/monitor" element={<ExecutionMonitor />} />
        <Route path="/results" element={<ResultsViewer />} />
      </Routes>
    </Layout>
  )
}
