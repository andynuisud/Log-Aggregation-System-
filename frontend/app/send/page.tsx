'use client'

import { useState } from 'react'
import '../globals.css'

const API_URL = 'http://localhost:5000/api/v1'

export default function SendLogs() {
  const [service, setService] = useState('')
  const [level, setLevel] = useState('INFO')
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState<string | null>(null)
  const now: Date = new Date();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if(!service || !level || !message){
      setStatus('error')
      return 
    }

    try {
      const res = await fetch(`${API_URL}/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, service, date: now, message }),
      })

      if (res.ok) {
        setStatus('sent')
        setMessage('')
      } else {
        setStatus('error')
      }
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="dashboard">
      <h1>Send Log</h1>

      <form className="send-form" onSubmit={handleSubmit}>
        <div className='form-group'>
          <label>Service Input</label>
          <input type="text" value={service} onChange={e => setService(e.target.value)} placeholder='ex: Service Type' />
          <label>Level Input</label>
          <select value={level} onChange={e => setLevel(e.target.value)}>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
          <label>Message Input</label>
          <input type="text" value={message} onChange={e => setMessage(e.target.value)} />
          <button className="submit-btn" type="submit">Submit</button>
          { status === 'error' && <p className="error-message">Error occured while submitting</p>}
        </div>
      </form>
    </div>
  )
}
