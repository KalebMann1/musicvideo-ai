// Upload screen - where artists upload their song and clips
// Copy and paste everything into frontend/src/pages/Upload.jsx

import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'

export default function Upload() {
  const navigate = useNavigate()
  const [song, setSong] = useState(null)
  const [artistClips, setArtistClips] = useState([])
  const [brollClips, setBrollClips] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const songRef = useRef()
  const artistRef = useRef()
  const brollRef = useRef()

  const handleSubmit = async () => {
    if (!song) return setError('Please upload a song')
    if (artistClips.length === 0 && brollClips.length === 0)
      return setError('Please upload at least one clip')

    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('song', song)
      artistClips.forEach(clip => formData.append('artist_clips', clip))
      brollClips.forEach(clip => formData.append('broll_clips', clip))

      const res = await axios.post(`${API}/upload`, formData)
      navigate(`/processing/${res.data.project_id}`)
    } catch (err) {
      setError('Upload failed. Make sure your backend is running.')
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.logo}>CLIPAI</h1>
        <p style={styles.tagline}>AI-Powered Music Video Editor</p>
      </div>

      {/* Upload Card */}
      <div style={styles.card}>

        {/* Song Upload */}
        <div style={styles.section}>
          <label style={styles.label}>YOUR SONG</label>
          <div
            style={{ ...styles.dropzone, ...(song ? styles.dropzoneActive : {}) }}
            onClick={() => songRef.current.click()}
          >
            {song ? (
              <div style={styles.fileInfo}>
                <span style={styles.fileIcon}>♪</span>
                <span style={styles.fileName}>{song.name}</span>
              </div>
            ) : (
              <div style={styles.dropPrompt}>
                <span style={styles.dropIcon}>♪</span>
                <span>Click to upload MP3 or WAV</span>
              </div>
            )}
          </div>
          <input
            ref={songRef}
            type="file"
            accept=".mp3,.wav"
            style={{ display: 'none' }}
            onChange={e => setSong(e.target.files[0])}
          />
        </div>

        {/* Artist Clips Upload */}
        <div style={styles.section}>
          <label style={styles.label}>ARTIST CLIPS
            <span style={styles.labelNote}> — lip sync clips filmed to the song</span>
          </label>
          <div
            style={{ ...styles.dropzone, ...(artistClips.length > 0 ? styles.dropzoneActive : {}) }}
            onClick={() => artistRef.current.click()}
          >
            {artistClips.length > 0 ? (
              <div style={styles.fileList}>
                {artistClips.map((c, i) => (
                  <div key={i} style={styles.fileChip}>▶ {c.name}</div>
                ))}
                <span style={styles.addMore}>+ Add more</span>
              </div>
            ) : (
              <div style={styles.dropPrompt}>
                <span style={styles.dropIcon}>▶</span>
                <span>Click to upload artist clips (MP4, MOV)</span>
              </div>
            )}
          </div>
          <input
            ref={artistRef}
            type="file"
            accept=".mp4,.mov,.avi"
            multiple
            style={{ display: 'none' }}
            onChange={e => setArtistClips(prev => [...prev, ...Array.from(e.target.files)])}
          />
        </div>

        {/* B-Roll Upload */}
        <div style={styles.section}>
          <label style={styles.label}>B-ROLL CLIPS
            <span style={styles.labelNote}> — filler clips, no lip sync needed</span>
          </label>
          <div
            style={{ ...styles.dropzone, ...(brollClips.length > 0 ? styles.dropzoneActive : {}) }}
            onClick={() => brollRef.current.click()}
          >
            {brollClips.length > 0 ? (
              <div style={styles.fileList}>
                {brollClips.map((c, i) => (
                  <div key={i} style={styles.fileChip}>▶ {c.name}</div>
                ))}
                <span style={styles.addMore}>+ Add more</span>
              </div>
            ) : (
              <div style={styles.dropPrompt}>
                <span style={styles.dropIcon}>◈</span>
                <span>Click to upload B-roll clips (MP4, MOV)</span>
              </div>
            )}
          </div>
          <input
            ref={brollRef}
            type="file"
            accept=".mp4,.mov,.avi"
            multiple
            style={{ display: 'none' }}
            onChange={e => setBrollClips(prev => [...prev, ...Array.from(e.target.files)])}
          />
        </div>

        {/* Error */}
        {error && <p style={styles.error}>{error}</p>}

        {/* Submit */}
        <button
          style={{ ...styles.button, ...(loading ? styles.buttonDisabled : {}) }}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'UPLOADING...' : 'GENERATE MUSIC VIDEO'}
        </button>
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
  },
  header: {
    textAlign: 'center',
    marginBottom: '48px',
  },
  logo: {
    fontSize: '72px',
    color: 'var(--gold)',
    lineHeight: 1,
    letterSpacing: '0.1em',
  },
  tagline: {
    color: 'var(--text-dim)',
    fontSize: '13px',
    letterSpacing: '0.2em',
    textTransform: 'uppercase',
    marginTop: '8px',
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '40px',
    width: '100%',
    maxWidth: '600px',
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  label: {
    fontSize: '11px',
    letterSpacing: '0.15em',
    color: 'var(--gold)',
    textTransform: 'uppercase',
  },
  labelNote: {
    color: 'var(--text-dim)',
    textTransform: 'none',
    letterSpacing: '0',
    fontSize: '11px',
  },
  dropzone: {
    border: '1px dashed var(--border)',
    borderRadius: '4px',
    padding: '24px',
    cursor: 'pointer',
    transition: 'border-color 0.2s',
    minHeight: '80px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dropzoneActive: {
    borderColor: 'var(--gold-dim)',
    borderStyle: 'solid',
  },
  dropPrompt: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    color: 'var(--text-dim)',
    fontSize: '13px',
  },
  dropIcon: {
    fontSize: '24px',
    color: 'var(--border)',
  },
  fileInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  fileIcon: {
    fontSize: '20px',
    color: 'var(--gold)',
  },
  fileName: {
    fontSize: '14px',
    color: 'var(--text)',
  },
  fileList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    alignItems: 'center',
  },
  fileChip: {
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: '2px',
    padding: '4px 10px',
    fontSize: '12px',
    color: 'var(--text)',
  },
  addMore: {
    fontSize: '12px',
    color: 'var(--gold-dim)',
  },
  error: {
    color: 'var(--error)',
    fontSize: '13px',
  },
  button: {
    background: 'var(--gold)',
    color: '#0a0a0a',
    border: 'none',
    borderRadius: '2px',
    padding: '16px',
    fontSize: '13px',
    fontWeight: '500',
    letterSpacing: '0.15em',
    width: '100%',
    transition: 'opacity 0.2s',
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
}