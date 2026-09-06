import { useEffect, useState, type FormEvent } from 'react'
import { Activity, AlertTriangle, ArrowUpRight, LogOut, MapPinned, RefreshCw, ShieldCheck, Users, X } from 'lucide-react'
import { Alert, Incident, Role, getAlerts, getCurrentUser, getIncidents, login, logout, performIncidentAction, User } from './api'

const demoAccounts: Array<{ label: string; username: string; role: Role }> = [
  { label: 'Supervisor', username: 'demo_alex_mwangi', role: 'SUPERVISOR' },
  { label: 'Ranger', username: 'demo_jane_kipchoge', role: 'RANGER' },
  { label: 'Community member', username: 'demo_grace_kisumu', role: 'COMMUNITY_MEMBER' },
  { label: 'Admin', username: 'admin', role: 'ADMIN' },
]

const actionLabels: Record<string, string> = {
  review: 'Review', verify: 'Verify', reject: 'Reject', dispatch: 'Dispatch',
  respond: 'Respond', resolve: 'Resolve', close: 'Close',
}

const navItems = [
  { label: 'Command center', icon: Activity },
  { label: 'Incident map', icon: MapPinned },
  { label: 'Response queue', icon: ShieldCheck },
  { label: 'Analytics', icon: ArrowUpRight },
]

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null)
  const [activeView, setActiveView] = useState('Command center')
  const [showAlerts, setShowAlerts] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function loadDashboard() {
    setLoading(true)
    setError('')
    try {
      const [nextIncidents, nextAlerts] = await Promise.all([getIncidents(), getAlerts()])
      setIncidents(nextIncidents)
      setAlerts(nextAlerts)
      setSelectedIncident((current) => current ? nextIncidents.find((incident) => incident.id === current.id) ?? current : null)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Could not load the command center.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (localStorage.getItem('wildguard_access_token')) {
      getCurrentUser().then(setUser).catch(() => logout())
    }
  }, [])

  useEffect(() => {
    if (user) loadDashboard()
  }, [user])

  if (!user) return <LoginScreen onLogin={setUser} />

  const activeIncidents = incidents.filter((incident) => !['RESOLVED', 'CLOSED', 'REJECTED'].includes(incident.status))
  const criticalIncidents = incidents.filter((incident) => incident.risk_level === 'CRITICAL')
  const canAct = user.role !== 'COMMUNITY_MEMBER'

  async function handleAction(action: string) {
    if (!selectedIncident) return
    setError('')
    try {
      const updated = await performIncidentAction(selectedIncident.id, action)
      setIncidents((current) => current.map((incident) => incident.id === updated.id ? updated : incident))
      setSelectedIncident(updated)
      setAlerts(await getAlerts())
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : 'This action could not be completed.')
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">W</div><div><strong>WILDGUARD</strong><span>KENYA</span></div></div>
        <div className="demo-label">DEMO DATA <span>NOT LIVE FIELD DATA</span></div>
        <nav>{navItems.map(({ label, icon: Icon }) => <button key={label} className={activeView === label ? 'active' : ''} onClick={() => setActiveView(label)}><Icon size={17} /> {label}</button>)}</nav>
        <div className="sidebar-foot"><div className="avatar">{initials(user)}</div><div><b>{displayName(user)}</b><small>{roleLabel(user.role)}</small></div><span className="status-dot" /></div>
      </aside>
      <section className="content">
        <header className="topbar"><div><p className="eyebrow">{new Date().toLocaleDateString('en-GB', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' }).toUpperCase()}</p><h1>{activeView}</h1></div><div className="top-actions"><button className="alert-button" onClick={() => setShowAlerts(true)}><AlertTriangle size={17} /> {alerts.length} critical alert{alerts.length === 1 ? '' : 's'}</button><button className="logout-button" onClick={() => { logout(); setUser(null) }} title="Sign out"><LogOut size={16} /></button></div></header>
        {error && <div className="error-banner" role="alert">{error}<button onClick={() => setError('')} aria-label="Dismiss error"><X size={15} /></button></div>}
        <div className="metrics"><Metric label="Active incidents" value={String(activeIncidents.length)} note="From the API" tone="green" /><Metric label="Critical now" value={String(criticalIncidents.length).padStart(2, '0')} note="Needs attention" tone="red" /><Metric label="Avg. response" value="42m" note="Demo metric" tone="amber" /><Metric label="Verified reports" value={`${incidents.length ? Math.round((incidents.filter((incident) => incident.verified).length / incidents.length) * 100) : 0}%`} note={`${incidents.length} loaded incidents`} tone="blue" /></div>
        <div className="workspace-grid">
          <section className="map-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE SITUATION</p><h2>Incident map</h2></div><button className="filter-button" onClick={loadDashboard}><RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh</button></div><div className="map"><div className="map-lines" />{incidents.map((incident, index) => <button key={incident.id} className={`map-pin ${incident.risk_level.toLowerCase()} ${selectedIncident?.id === incident.id ? 'selected' : ''}`} style={{ left: `${18 + ((index * 29) % 68)}%`, top: `${22 + ((index * 23) % 55)}%` }} onClick={() => setSelectedIncident(incident)} title={`Open incident ${incident.id}`} aria-label={`Open ${incident.species.name} incident`}><span /></button>)}<div className="map-legend"><span><i className="critical" /> Critical</span><span><i className="high" /> High</span><span><i className="moderate" /> Moderate</span></div><div className="map-caption">Kenya · {incidents.length} API incidents</div></div></section>
          <section className="feed-panel"><div className="panel-heading"><div><p className="eyebrow">REQUIRES ACTION</p><h2>Incident feed</h2></div><span className="feed-count">{incidents.length}</span></div><div className="incident-list">{incidents.map((incident) => <button className={`incident ${selectedIncident?.id === incident.id ? 'selected' : ''}`} key={incident.id} onClick={() => setSelectedIncident(incident)}><div className={`severity-bar ${incident.risk_level.toLowerCase()}`} /><div className="incident-main"><div className="incident-title"><b>{incident.species.name}</b><span className={`level ${incident.risk_level.toLowerCase()}`}>{incident.risk_level}</span></div><p>{incident.description}</p><div className="incident-meta"><span>{incident.community.name}</span><span>{formatTime(incident.event_time)}</span></div></div><span className="incident-id">WG-{String(incident.id).padStart(4, '0')}</span></button>)}</div></section>
        </div>
        <section className="bottom-row"><div className="trend-panel"><div className="panel-heading"><div><p className="eyebrow">FIELD PULSE</p><h2>Reports this month</h2></div><span className="trend-value">Live API <small>demo data</small></span></div><div className="bars">{[38, 52, 45, 67, 59, 76, 62, 84, 71, 91, 78, 96].map((height, index) => <div className="bar-wrap" key={index}><div className="bar" style={{ height: `${height}%` }} /><small>{index + 1}</small></div>)}</div></div><div className="communities-panel"><div className="panel-heading"><div><p className="eyebrow">NETWORK</p><h2>Communities</h2></div><Users size={19} /></div>{topCommunities(incidents).map(([name, count]) => <div className="community-row" key={name}><span>{name}</span><b>{count} <small>reports</small></b></div>)}</div></section>
      </section>
      {selectedIncident && <IncidentDrawer incident={selectedIncident} canAct={canAct} onClose={() => setSelectedIncident(null)} onAction={handleAction} />}
      {showAlerts && <div className="modal-backdrop" onClick={() => setShowAlerts(false)}><section className="alerts-modal" onClick={(event) => event.stopPropagation()}><div className="panel-heading"><div><p className="eyebrow">COMMAND CENTER</p><h2>Critical alerts</h2></div><button className="icon-button" onClick={() => setShowAlerts(false)} aria-label="Close alerts"><X size={17} /></button></div>{alerts.length ? alerts.map((alert) => <article className="alert-row" key={alert.id}><AlertTriangle size={17} /><div><b>{alert.title}</b><p>{alert.message}</p><small>{formatTime(alert.created_at)}</small></div></article>) : <p className="empty-state">No critical alerts are currently available.</p>}</section></div>}
    </main>
  )
}

function LoginScreen({ onLogin }: { onLogin: (user: User) => void }) {
  const [username, setUsername] = useState('demo_alex_mwangi')
  const [password, setPassword] = useState('password')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault(); setLoading(true); setError('')
    try { onLogin(await login(username, password)) } catch (loginError) { setError(loginError instanceof Error ? loginError.message : 'Sign in failed.') } finally { setLoading(false) }
  }

  return <main className="login-shell"><form className="login-card" onSubmit={submit}><div className="brand login-brand"><div className="brand-mark">W</div><div><strong>WILDGUARD</strong><span>KENYA</span></div></div><p className="eyebrow">DEMO COMMAND CENTER</p><h1>Sign in to respond.</h1><p className="login-copy">Use a demo role to explore the operational workflow.</p><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label><label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /></label>{error && <div className="login-error" role="alert">{error}</div>}<button className="login-submit" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button><div className="demo-accounts"><span>Quick demo access</span>{demoAccounts.map((account) => <button type="button" key={account.username} onClick={() => { setUsername(account.username); setPassword(account.username === 'admin' ? 'admin123' : 'password') }}>{account.label}</button>)}</div></form></main>
}

function IncidentDrawer({ incident, canAct, onClose, onAction }: { incident: Incident; canAct: boolean; onClose: () => void; onAction: (action: string) => void }) {
  const actions = nextActions(incident.status)
  return <aside className="incident-drawer"><div className="drawer-header"><div><p className="eyebrow">INCIDENT WG-{String(incident.id).padStart(4, '0')}</p><h2>{incident.species.name} near {incident.community.name}</h2></div><button className="icon-button" onClick={onClose} aria-label="Close incident"><X size={17} /></button></div><div className={`risk-callout ${incident.risk_level.toLowerCase()}`}><span>Risk score</span><strong>{incident.risk_score}/100</strong><b>{incident.risk_level}</b></div><p className="drawer-description">{incident.description}</p><dl className="incident-facts"><div><dt>Status</dt><dd>{incident.status.replace('_', ' ')}</dd></div><div><dt>Animals</dt><dd>{incident.animal_count}</dd></div><div><dt>Community</dt><dd>{incident.community.county}</dd></div><div><dt>Reported</dt><dd>{formatTime(incident.created_at)}</dd></div></dl>{canAct && actions.length > 0 ? <div className="drawer-actions"><p className="eyebrow">NEXT WORKFLOW STEP</p>{actions.map((action) => <button key={action} onClick={() => onAction(action)}>{actionLabels[action]}</button>)}</div> : <p className="drawer-note">{canAct ? 'This incident is at the end of its workflow.' : 'Community members can view incidents. Ranger and supervisor accounts can advance the workflow.'}</p>}</aside>
}

function nextActions(status: Incident['status']) { return ({ REPORTED: ['review'], UNDER_REVIEW: ['verify', 'reject'], VERIFIED: ['dispatch'], DISPATCHED: ['respond'], RESPONDING: ['resolve'], RESOLVED: ['close'] } as Record<string, string[]>)[status] ?? [] }
function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone: string }) { return <div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></div> }
function displayName(user: User) { return `${user.first_name} ${user.last_name}`.trim() || user.username }
function initials(user: User) { return displayName(user).split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase() }
function roleLabel(role: Role) { return role.replace('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) }
function formatTime(value: string) { return new Date(value).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) }
function topCommunities(incidents: Incident[]) { const counts = incidents.reduce<Record<string, number>>((all, incident) => ({ ...all, [incident.community.name]: (all[incident.community.name] ?? 0) + 1 }), {}); return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3) }

export default App
