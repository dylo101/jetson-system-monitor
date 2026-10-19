import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Sample = {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  uptime_seconds: number;
  temperature_c: number | null;
};
type Health = { status: string; sample_interval_seconds: number };

async function get<T,>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal });
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

function CpuChart({ samples }: { samples: Sample[] }) {
  if (samples.length === 0) return <p>No history yet. Samples appear after collection succeeds.</p>;
  const first = Date.parse(samples[0].timestamp);
  const last = Date.parse(samples[samples.length - 1].timestamp);
  const points = samples.map(s => `${40 + (Date.parse(s.timestamp) - first) / Math.max(1, last - first) * 920},${220 - s.cpu_percent * 1.9}`).join(' ');
  return <>
    <svg viewBox="0 0 1000 250" role="img" aria-label="CPU usage over time, zero to one hundred percent">
      {[0, 50, 100].map(value => <g key={value}>
        <line x1="40" x2="960" y1={220 - value * 1.9} y2={220 - value * 1.9} stroke="#2b3a4b" />
        <text x="0" y={225 - value * 1.9} fill="#93a5ba" fontSize="14">{value}</text>
      </g>)}
      <polyline points={points} fill="none" stroke="#6ee7bd" strokeWidth="3" />
      {samples.length === 1 && <circle cx="40" cy={220 - samples[0].cpu_percent * 1.9} r="4" fill="#6ee7bd" />}
    </svg>
    <div className="axis"><span>{new Date(first).toLocaleTimeString()}</span><span>{new Date(last).toLocaleTimeString()}</span></div>
  </>;
}

function App() {
  const [current, setCurrent] = useState<Sample | null>(null);
  const [history, setHistory] = useState<Sample[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState('');
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    async function refresh() {
      try {
        const [sample, samples, status] = await Promise.all([
          get<Sample>('/api/metrics/current', controller.signal),
          get<Sample[]>('/api/metrics/history', controller.signal),
          get<Health>('/api/health', controller.signal),
        ]);
        setCurrent(sample);
        setHistory(samples);
        setHealth(status);
        setError('');
      } catch (e) {
        if (!controller.signal.aborted) setError(e instanceof Error ? e.message : 'Connection failed');
      } finally {
        if (!controller.signal.aborted) timer = setTimeout(refresh, 5000);
      }
    }
    void refresh();
    const clock = setInterval(() => setNow(Date.now()), 1000);
    return () => { controller.abort(); clearTimeout(timer); clearInterval(clock); };
  }, []);

  const stale = current && now - Date.parse(current.timestamp) > Math.max(15, (health?.sample_interval_seconds ?? 5) * 3) * 1000;
  const status = error ? 'Disconnected' : stale || health?.status === 'degraded' ? 'Needs attention' : current ? 'Live' : 'Connecting';
  const cards = current ? [
    ['CPU usage', `${current.cpu_percent.toFixed(1)}%`, 'Across all CPU cores'],
    ['Memory', `${current.memory_percent.toFixed(1)}%`, 'System RAM in use'],
    ['Disk', `${current.disk_percent.toFixed(1)}%`, 'Root filesystem in use'],
    ['CPU temperature', current.temperature_c === null ? 'Unavailable' : `${current.temperature_c.toFixed(1)}°C`, 'Available CPU sensor'],
    ['Uptime', `${Math.floor(current.uptime_seconds / 3600)}h ${Math.floor(current.uptime_seconds % 3600 / 60)}m`, 'Since the host last booted'],
  ] : [];

  return <main>
    <header>
      <div><p className="eyebrow">HOST OBSERVABILITY / PROTOTYPE</p><h1>Jetson System Monitor</h1><p className="muted">A clear view of your Linux host.</p></div>
      <span className={`status ${status === 'Live' ? 'live' : ''}`}>{status}</span>
    </header>
    {error && <p role="alert" className="notice">Cannot refresh metrics: {error}. Check that the API is running. Retrying every five seconds.</p>}
    {stale && <p role="alert" className="notice">These readings are stale. The last successful sample is shown below.</p>}
    {!current && !error && <p role="status">Loading the first sample…</p>}
    <section className="cards" aria-label="Current host metrics">
      {cards.map(([title, value, detail]) => <article key={title}><h2>{title}</h2><strong>{value}</strong><p>{detail}</p></article>)}
    </section>
    <section className="chart">
      <div className="chart-heading"><div><h2>CPU activity</h2><p className="muted">Most recent hour · up to 720 samples · 0–100%</p></div><span>{history.length} samples</span></div>
      <CpuChart samples={history} />
    </section>
    <footer><span>Last sample: {current ? new Date(current.timestamp).toLocaleString() : 'Waiting'}</span><span>Read-only host metrics · refreshes every 5s</span></footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
