import { useEffect, useRef, useState, useCallback } from 'react'
import type { WsMessage } from '../types'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState<WsMessage[]>([])
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL)

      ws.current.onopen = () => setConnected(true)

      ws.current.onmessage = (e) => {
        try {
          const msg: WsMessage = JSON.parse(e.data)
          setMessages(prev => [msg, ...prev].slice(0, 100))
        } catch { /* skip non-JSON */ }
      }

      ws.current.onclose = () => {
        setConnected(false)
        reconnectTimer.current = setTimeout(connect, 3000)
      }

      ws.current.onerror = () => ws.current?.close()
    } catch { /* connection failed, will retry */ }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      ws.current?.close()
    }
  }, [connect])

  return { connected, messages, lastMessage: messages[0] ?? null }
}
