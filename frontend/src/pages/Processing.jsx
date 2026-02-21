// Processing screen - polls backend every 5 seconds to check render status
// Copy and paste everything into frontend/src/pages/Processing.jsx

import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'

const STEPS = [
  'Analyzing your song...',
  'Scanning your clips...',
  'Detecting lip sync positions...',
  'Placing B-roll clips...',
  'Rendering your music video...',
]

export default function Processing() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [stepIndex, setStepIndex] = useState(0)
  const [statusMsg, setStatusMsg] = useState('Starting...')
  const [error, setError] = useState('')

  useEffect(() => {
    // Start the render job immediately
    axios.post(`${API}/render/${projectId}`).catch(() => {})

    // Cycle through steps visually
    const stepInterval = setInterval(() => {
      setStepIndex(prev => (prev < STEPS.length - 1 ? prev + 1 : prev))
    }, 6000)

    // Poll status every 5 seconds
    const pollInterval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/status/${projectId}`)
        setStatusMsg(res.data.message)

        if (res.data.status === 'done') {
          clearInterval(pollInterval)
          clearInterval(stepInterval)
          navigate(`/preview/${projectId}`)
        }

        if (res.data.status === 'error') {
          clearInterval(pollInterval)
          clearInterval(stepInterval)
          setError(res.data.message)
        }
      } catch (err) {
        // Keep polling even if one request fails
      }
    }, 5000)

    return () => {
      clearInterval(pollInterval)
      clearInterval(stepInterval)
    }
  }, [projectId])

  return (
    <div style={styles.page}>
      <h1 style={styles.logo}>CLIPAI</h1>

      <div style={styles.card}>
        <div style={styles.spinner} />

        <h2 style={styles.heading}>BUILDING YOUR VIDEO</h2>

        <div style={styles.steps}>
          {STEPS.map((step, i) => (
            <div key={i} style={{
              ...styles.step,
              color: i === stepIndex
                ? 'var(--gold)'
                : i < stepIndex
                  ? 'var(--text-dim)'
                  : 'var(--border)'
            }}>
              <span style={styles.stepDot}>
                {i < stepIndex ? '✓' : i === stepIndex ? '▶' : '○'}
              </span>
              {step}
            </div>
          ))}
        </div>

        <p style={styles.status}>{statusMsg}</p>

        {error && <p style={styles.error}>Error: {error}</p>}

        <p style={styles.note}>This takes a few minutes. Don't close this tab.</p>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    gap: '32px',
  },
  logo: {
    fontSize: '48px',
    color: 'var(--gold)',
    letterSpacing: '0.1em',
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '48px',
    width: '100%',
    maxWidth: '480px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '24px',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '2px solid var(--border)',
    borderTop: '2px solid var(--gold)',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  heading: {
    fontSize: '28px',
    color: 'var(--text)',
    letterSpacing: '0.1em',
  },
  steps: {
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
    width: '100%',
  },
  step: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '13px',
    letterSpacing: '0.05em',
    transition: 'color 0.4s',
  },
  stepDot: {
    fontSize: '11px',
    width: '16px',
  },
  status: {
    color: 'var(--gold-dim)',
    fontSize: '12px',
    letterSpacing: '0.05em',
  },
  note: {
    color: 'var(--text-dim)',
    fontSize: '12px',
    letterSpacing: '0.05em',
  },
  error: {
    color: 'var(--error)',
    fontSize: '13px',
    textAlign: 'center',
  },
}