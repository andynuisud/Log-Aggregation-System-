'use client'

import { useState, useEffect } from 'react'
import './globals.css'

interface LogEntry {
  id?: number
  date?: string
  level?: string
  service?: string
  message?: string
}

const API_URL = 'http://localhost:5000/api/v1'

export default function Dashboard() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [total, setTotal] = useState(0)
  const [filterLevel, setFilterLevel] = useState('ALL')
  const [filterService, setFilterService] = useState('ALL')
  const [filterMessage, setFilterMessage] = useState('')
  const [services, setServices] = useState<string[]>([])

  const fetchLogs = async () => {
    try {
      const params = new URLSearchParams()
      if (filterLevel !== 'ALL') params.set('level', filterLevel)
      if (filterService !== 'ALL') params.set('service', filterService)
      if (filterMessage) params.set('message', filterMessage)
      const res = await fetch(`${API_URL}/logs?${params.toString()}`)
      const data = await res.json()
      setLogs(data.logs)
      setTotal(data.total)
    } catch (err) {
      console.error('Failed to fetch logs:', err)
    }
  }

  const fetchServices = async () => {
    try {
      const res = await fetch(`${API_URL}/services`)
      const data: string[] = await res.json()
      setServices(data)
    } catch (err) {
      console.error('Failed to fetch services:', err)
    }
  }

  const populateLogs = async () => {
    try {
      await fetch(`${API_URL}/logs/populate`, { method: 'POST' })
    } catch (err) {
      console.error('Failed to populate logs:', err)
    }
  }

  const clearLogs = async () => {
    try {
      await fetch(`${API_URL}/logs`, { method: 'DELETE' })
    } catch (err) {
      console.error('Failed to clear logs:', err)
    }
  }

  const deleteLog = async (id: number) => {
    try {
      await fetch(`${API_URL}/logs/${id}`, { method: 'DELETE' })
      fetchLogs()
    } catch (err) {
      console.error('Failed to delete log:', err)
    }
  }


  useEffect(() => {
    fetchLogs()
    fetchServices()
    const interval = setInterval(fetchLogs, 5000)
    return () => clearInterval(interval)
  }, [filterLevel, filterService, filterMessage])

  const serviceOptions = ['ALL', ...services]
  const levelOptions = ['ALL', 'INFO', 'WARN', 'ERROR']

  const counts = {
    total: total,
    error: logs.filter(l => l.level === 'ERROR').length,
    warn: logs.filter(l => l.level === 'WARN').length,
    info: logs.filter(l => l.level === 'INFO').length,
  }

  return (
    <div className="dashboard">
      <h1>Log Dashboard</h1>

      <div className="stats">
        <div className="stat-card">
          <div className="count">{counts.total}</div>
          <div className="label">Total</div>
        </div>
        <div className="stat-card">
          <div className="count">{counts.error}</div>
          <div className="label">Errors</div>
        </div>
        <div className="stat-card">
          <div className="count">{counts.warn}</div>
          <div className="label">Warnings</div>
        </div>
        <div className="stat-card">
          <div className="count">{counts.info}</div>
          <div className="label">Info</div>
        </div>
      </div>

      <div className="filters">
        <select value={filterLevel} onChange={e => setFilterLevel(e.target.value)}>
          {levelOptions.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
        <select value={filterService} onChange={e => setFilterService(e.target.value)}>
          {serviceOptions.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={async () => { await populateLogs(); await fetchLogs(); }}>Populate Logs</button>
        <button onClick={async () => { await clearLogs(); await fetchLogs(); }}>Clear Logs</button>
        <a href="/send" className="nav-btn">Send Log</a>
        <input className="filter-input" value={filterMessage} type="text" placeholder="Search messages..." onChange={e => setFilterMessage(e.target.value)} />
      </div>

      {logs.length === 0 ? (
        <div className="empty">No logs to display</div>
      ) : (
        <div className="log-table-wrapper">
          <table className="log-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Service</th>
                <th>Message</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {logs.slice().reverse().map((log, i) => (
                <tr key={i}>
                  <td>{log.id ?? '—'}</td>
                  <td>{log.date || '—'}</td>
                  <td><span className={`level-badge level-${log.level || 'INFO'}`}>{log.level || 'INFO'}</span></td>
                  <td>{log.service || 'unknown'}</td>
                  <td>{log.message || '—'}</td>
                  <td><button className="delete-btn" onClick={() => log.id && deleteLog(log.id)}>x</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
