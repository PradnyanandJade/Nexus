import { useState } from 'react'
import { login, register } from '../services/authService'

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ username: '', password: '' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const session = mode === 'login' ? await login(form) : await register(form)
      onAuthenticated(session)
    } catch (reason) {
      setError(reason.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-screen">
      <div className="auth-visual">
        {/* <span className="auth-stamp">N / 02</span>  */}
        {/* <div className="orbit" /> */}
        <div className="quote">
          "The best answer
          <br />
          <i>
            has somewhere
            <br />
            to go back to.
          </i>"
        </div> 
        <span className="caption">
          A grounded intelligence
          <br />
          for curious work.
        </span>
      </div>
      <form className="auth-card" onSubmit={submit}>
        <div className="brand dark">
          <b>N</b>
          <span>
            NEXUS 
          </span>
        </div>
        <span className="eyebrow">PRIVATE RESEARCH DESK</span>
        <h1>{mode === 'login' ? 'Welcome back.' : 'Start a new desk.'}</h1>
        <p>
          {mode === 'login'
            ? 'Pick up where your thinking left off.'
            : 'A quiet place to ask better questions.'}
        </p>
        <label>
          USERNAME
          <input
            required
            minLength="3"
            value={form.username}
            onChange={(event) => setForm({ ...form, username: event.target.value })}
            placeholder="your name"
          />
        </label>
        <label>
          PASSWORD
          <input
            required
            minLength="3"
            type="password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            placeholder="********"
          />
        </label>
        {error && <div className="form-error">{error}</div>}
        <button className="submit" disabled={busy}>
          {busy
            ? 'Connecting...'
            : mode === 'login'
              ? 'Enter workspace ↗'
              : 'Create workspace ↗'}
        </button>
        <button
          type="button"
          className="mode-switch"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login'
            ? 'Need a workspace? Register'
            : 'Already have a workspace? Sign in'}
        </button>
        <small className="auth-footnote">
          Your documents stay scoped to your account.
        </small>
      </form>
    </main>
  )
}
