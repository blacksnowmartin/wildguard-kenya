import { Activity, AlertTriangle, ArrowUpRight, MapPinned, ShieldCheck, Users } from 'lucide-react'

type Incident = {
  id: string
  species: string
  community: string
  level: 'CRITICAL' | 'HIGH' | 'MODERATE'
  time: string
  description: string
  x: string
  y: string
}

const incidents: Incident[] = [
  { id: 'WG-0248', species: 'Elephant', community: 'Mara North', level: 'CRITICAL', time: '12 min ago', description: 'Herd reported close to cultivated land.', x: '63%', y: '33%' },
  { id: 'WG-0247', species: 'Buffalo', community: 'Kajiado East', level: 'HIGH', time: '46 min ago', description: 'Livestock enclosure breached overnight.', x: '27%', y: '58%' },
  { id: 'WG-0246', species: 'Lion', community: 'Tsavo West', level: 'HIGH', time: '2 hr ago', description: 'Tracks found along the community boundary.', x: '74%', y: '68%' },
  { id: 'WG-0245', species: 'Hippo', community: 'Lake Naivasha', level: 'MODERATE', time: '4 hr ago', description: 'Sighting near a water access path.', x: '46%', y: '43%' },
]

function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">W</div><div><strong>WILDGUARD</strong><span>KENYA</span></div></div>
        <div className="demo-label">DEMO DATA <span>NOT LIVE FIELD DATA</span></div>
        <nav><a className="active"><Activity size={17} /> Command center</a><a><MapPinned size={17} /> Incident map</a><a><ShieldCheck size={17} /> Response queue</a><a><ArrowUpRight size={17} /> Analytics</a></nav>
        <div className="sidebar-foot"><div className="avatar">AM</div><div><b>Alex Mwangi</b><small>Supervisor</small></div><span className="status-dot" /></div>
      </aside>
      <section className="content">
        <header className="topbar"><div><p className="eyebrow">THURSDAY, 27 AUGUST 2026</p><h1>Command center</h1></div><button className="alert-button"><AlertTriangle size={17} /> 1 critical alert</button></header>
        <div className="metrics"><Metric label="Active incidents" value="18" note="+3 this week" tone="green" /><Metric label="Critical now" value="03" note="Needs attention" tone="red" /><Metric label="Avg. response" value="42m" note="8m faster this week" tone="amber" /><Metric label="Verified reports" value="87%" note="Across 24 communities" tone="blue" /></div>
        <div className="workspace-grid">
          <section className="map-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE SITUATION</p><h2>Incident map</h2></div><button className="filter-button">Last 30 days <span>⌄</span></button></div><div className="map"><div className="map-lines" />{incidents.map((incident) => <div key={incident.id} className={`map-pin ${incident.level.toLowerCase()}`} style={{ left: incident.x, top: incident.y }} title={incident.id}><span /></div>)}<div className="map-legend"><span><i className="critical" /> Critical</span><span><i className="high" /> High</span><span><i className="moderate" /> Moderate</span></div><div className="map-caption">Kenya · 24 monitored communities</div></div></section>
          <section className="feed-panel"><div className="panel-heading"><div><p className="eyebrow">REQUIRES ACTION</p><h2>Incident feed</h2></div><button className="icon-button" aria-label="View all incidents">•••</button></div><div className="incident-list">{incidents.map((incident) => <article className="incident" key={incident.id}><div className={`severity-bar ${incident.level.toLowerCase()}`} /><div className="incident-main"><div className="incident-title"><b>{incident.species}</b><span className={`level ${incident.level.toLowerCase()}`}>{incident.level}</span></div><p>{incident.description}</p><div className="incident-meta"><span>{incident.community}</span><span>{incident.time}</span></div></div><span className="incident-id">{incident.id}</span></article>)}</div></section>
        </div>
        <section className="bottom-row"><div className="trend-panel"><div className="panel-heading"><div><p className="eyebrow">FIELD PULSE</p><h2>Reports this month</h2></div><span className="trend-value">+14.6% <small>vs last month</small></span></div><div className="bars">{[38, 52, 45, 67, 59, 76, 62, 84, 71, 91, 78, 96].map((height, index) => <div className="bar-wrap" key={index}><div className="bar" style={{ height: `${height}%` }} /><small>{index + 1}</small></div>)}</div></div><div className="communities-panel"><div className="panel-heading"><div><p className="eyebrow">NETWORK</p><h2>Communities</h2></div><Users size={19} /></div><div className="community-row"><span>Mara North</span><b>12 <small>reports</small></b></div><div className="community-row"><span>Kajiado East</span><b>09 <small>reports</small></b></div><div className="community-row"><span>Tsavo West</span><b>07 <small>reports</small></b></div></div></section>
      </section>
    </main>
  )
}

function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone: string }) {
  return <div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></div>
}

export default App
