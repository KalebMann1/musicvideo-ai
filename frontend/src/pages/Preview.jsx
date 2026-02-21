// Preview screen - shows the rendered video and chat interface for revisions
// Copy and paste everything into frontend/src/pages/Preview.jsx

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

const API = 'http://127.0.0.1:8000/api'

export default function Preview() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([
    { role: 'ai', text: "Your music video is ready. Watch it and let me know what you'd like to change." }
  ])
  const [input, setInput] = useState('')

  const videoUrl = `${API}/download/${projectId}`

  const sendMessage = () => {
    if (!input.trim()) return
    setMessages(prev => [...prev, { role: 'user', text: input }])
    setMessages(prev => [...prev, { role: 'ai', text: 'Chat revision coming soon — this will be connected to AI in the next build.' }])
    setInput('')
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.logo} onClick={() => navigate('/')}>CLIPAI</h1>
        <a href={videoUrl} download="music_video.mp4" style={styles.downloadBtn}>
          DOWNLOAD
        </a>
      </div>

      {/* Main layout */}
      <div style={styles.main}>
        {/* Video player */}
        <div style={styles.videoSection}>
          <video
            controls
            style={styles.video}
            src={videoUrl}
          />
        </div>

        {/* Chat sidebar */}
        <div style={styles.chatSection}>
          <div style={styles.chatHeader}>
            <span style={styles.chatTitle}>REVISIONS</span>
            <span style={styles.chatSubtitle}>Tell the AI what to change</span>
          </div>

          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div key={i} style={{
                ...styles.message,
                ...(msg.role === 'user' ? styles.messageUser : styles.messageAi)
              }}>
                {msg.text}
              </div>
            ))}
          </div>

          <div style={styles.chatInput}>
            <input
              style={styles.input}
              placeholder="e.g. make the chorus faster..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
            />
            <button style={styles.sendBtn} onClick={sendMessage}>→</button>
          </div>
        </div>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 40px',
    borderBottom: '1px solid var(--border)',
  },
  logo: {
    fontSize: '32px',
    color: 'var(--gold)',
    cursor: 'pointer',
    letterSpacing: '0.1em',
  },
  downloadBtn: {
    background: 'transparent',
    border: '1px solid var(--gold)',
    color: 'var(--gold)',
    padding: '8px 20px',
    fontSize: '11px',
    letterSpacing: '0.15em',
    textDecoration: 'none',
    borderRadius: '2px',
  },
  main: {
    display: 'flex',
    flex: 1,
    height: 'calc(100vh - 73px)',
  },
  videoSection: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px',
    background: '#050505',
  },
  video: {
    maxWidth: '100%',
    maxHeight: '100%',
    borderRadius: '2px',
  },
  chatSection: {
    width: '340px',
    borderLeft: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--surface)',
  },
  chatHeader: {
    padding: '24px',
    borderBottom: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  chatTitle: {
    fontSize: '13px',
    letterSpacing: '0.15em',
    color: 'var(--gold)',
  },
  chatSubtitle: {
    fontSize: '12px',
    color: 'var(--text-dim)',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  message: {
    fontSize: '13px',
    lineHeight: '1.6',
    padding: '12px',
    borderRadius: '2px',
  },
  messageAi: {
    background: 'var(--bg)',
    color: 'var(--text)',
    border: '1px solid var(--border)',
  },
  messageUser: {
    background: 'var(--gold)',
    color: '#0a0a0a',
    alignSelf: 'flex-end',
    maxWidth: '85%',
  },
  chatInput: {
    padding: '16px',
    borderTop: '1px solid var(--border)',
    display: 'flex',
    gap: '8px',
  },
  input: {
    flex: 1,
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: '2px',
    padding: '10px 12px',
    color: 'var(--text)',
    fontSize: '13px',
    fontFamily: 'DM Sans, sans-serif',
    outline: 'none',
  },
  sendBtn: {
    background: 'var(--gold)',
    border: 'none',
    borderRadius: '2px',
    padding: '10px 14px',
    color: '#0a0a0a',
    fontSize: '16px',
  },
}