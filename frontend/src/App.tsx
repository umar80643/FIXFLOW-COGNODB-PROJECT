import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { Activity, ArrowRight, CircleGauge, Database, Layers3, Search, ShieldCheck, Sparkles, Wrench } from 'lucide-react';
import { Link, NavLink, Route, Routes, useNavigate, useParams } from 'react-router-dom';
import { loadDevice, loadGraph, loadHealth, loadInsights, loadRecommendation, loadRelatedDevices, searchDevices } from './api';
import { demoDevices } from './data';
import type { DeviceDetail, DeviceSummary, GraphResponse, Insight } from './types';

type Health = { status: string; database_connected: boolean; message: string };

const categories = ['All', 'Phone', 'Laptop', 'Console', 'Tablet'];

function App() {
  const [health, setHealth] = useState<Health>({ status: 'degraded', database_connected: false, message: 'Loading status...' });
  const [insights, setInsights] = useState<Insight[]>([]);

  useEffect(() => {
    void loadHealth().then(setHealth);
    void loadInsights().then(setInsights);
  }, []);

  return (
    <div className="app-shell">
      <Header health={health} />
      <main className="page-shell">
        <Routes>
          <Route path="/" element={<HomePage insights={insights} />} />
          <Route path="/device/:slug" element={<DevicePage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
    </div>
  );
}

function Header({ health }: { health: Health }) {
  return (
    <header className="topbar">
      <Link to="/" className="brand">
        <span className="brand-mark">F</span>
        <span>
          <strong>FixFlow</strong>
          <small>CognoDB repair graph</small>
        </span>
      </Link>
      <nav className="nav">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/explore">Explore</NavLink>
        <NavLink to="/about">About</NavLink>
      </nav>
      <div className={`health-pill ${health.database_connected ? 'good' : 'soft'}`}>
        <Database size={14} />
        <span>{health.database_connected ? 'Live graph connected' : 'Demo mode ready'}</span>
      </div>
    </header>
  );
}

function HomePage({ insights }: { insights: Insight[] }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const [devices, setDevices] = useState<DeviceSummary[]>(demoDevices);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    void searchDevices(query, category === 'All' ? undefined : category).then((items) => {
      if (active) {
        setDevices(items);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [query, category]);

  const spotlight = useMemo(() => devices.slice(0, 4), [devices]);

  return (
    <section className="stack">
      <section className="hero-card">
        <div className="hero-copy">
          <span className="eyebrow"><Sparkles size={14} /> Graph-first repair guidance</span>
          <h1>From symptom to fix path, in one connected view.</h1>
          <p>
            FixFlow uses a graph schema so device symptoms, causes, guides, parts, tools, and repair venues stay linked instead of buried in joins.
          </p>
          <div className="search-row">
            <div className="search-box">
              <Search size={18} />
              <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search devices, brands, or symptoms" />
            </div>
            <button className="primary-btn" onClick={() => navigate(`/device/${spotlight[0]?.slug ?? 'iphone-15'}`)}>
              Open device <ArrowRight size={16} />
            </button>
          </div>
          <div className="filters">
            {categories.map((item) => (
              <button key={item} className={item === category ? 'chip active' : 'chip'} onClick={() => setCategory(item)}>
                {item}
              </button>
            ))}
          </div>
        </div>
        <aside className="hero-aside">
          <div className="stat-grid">
            {insights.length ? insights.map((insight) => <StatCard key={insight.label} {...insight} />) : <p className="placeholder">Loading graph insights...</p>}
          </div>
          <div className="mini-graph">
            <GraphPreview />
          </div>
        </aside>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <span className="eyebrow"><Layers3 size={14} /> Devices</span>
            <h2>Browse connected devices</h2>
          </div>
          <span className="muted">{loading ? 'Updating results...' : `${devices.length} matched devices`}</span>
        </div>
        <div className="device-grid">
          {devices.map((device) => <DeviceCard key={device.id} device={device} />)}
        </div>
      </section>
    </section>
  );
}

function DeviceCard({ device }: { device: DeviceSummary }) {
  return (
    <Link className="device-card" to={`/device/${device.slug}`}>
      <div className="device-card-top">
        <div>
          <span className="device-brand">{device.brand}</span>
          <h3>{device.name}</h3>
        </div>
        <CircleGauge size={18} />
      </div>
      <div className="device-meta">
        <span>{device.category}</span>
        <span>{device.difficulty}</span>
        <span>{Math.round(device.confidence * 100)}% match</span>
      </div>
      <div className="device-bar"><span style={{ width: `${device.popularity}%` }} /></div>
    </Link>
  );
}

function DevicePage() {
  const params = useParams();
  const slug = params.slug ?? 'iphone-15';
  const [detail, setDetail] = useState<DeviceDetail | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [related, setRelated] = useState<DeviceSummary[]>([]);
  const [selectedSymptom, setSelectedSymptom] = useState<string>('');

  useEffect(() => {
    let active = true;
    void loadDevice(slug).then((data) => {
      if (active) {
        setDetail(data);
        setSelectedSymptom(data.symptoms[0]?.slug ?? '');
      }
    });
    void loadGraph(slug).then((data) => {
      if (active) setGraph(data);
    });
    void loadRelatedDevices(slug).then((items) => {
      if (active) setRelated(items);
    });
    return () => {
      active = false;
    };
  }, [slug]);

  useEffect(() => {
    if (!detail || !selectedSymptom) return;
    let active = true;
    void loadRecommendation(slug, selectedSymptom).then((data) => {
      if (active) setGraph(data.graph);
    });
    return () => {
      active = false;
    };
  }, [detail, selectedSymptom, slug]);

  if (!detail) {
    return <div className="section-card">Loading device...</div>;
  }

  return (
    <section className="stack">
      <section className="section-card hero-subtle">
        <div className="section-heading">
          <div>
            <span className="eyebrow"><ShieldCheck size={14} /> Device detail</span>
            <h2>{detail.device.name}</h2>
            <p className="muted">{detail.device.brand} · {detail.device.category} · {Math.round(detail.device.confidence * 100)}% confidence</p>
          </div>
          <Link className="ghost-btn" to="/explore">
            <Wrench size={16} /> Explore the graph
          </Link>
        </div>
        <div className="symptom-rail">
          {detail.symptoms.map((symptom) => (
            <button key={symptom.slug} className={symptom.slug === selectedSymptom ? 'symptom-card active' : 'symptom-card'} onClick={() => setSelectedSymptom(symptom.slug)}>
              <strong>{symptom.name}</strong>
              <span>{symptom.severity} severity · {symptom.likely_fix_time}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="triple-grid">
        <ContentPanel title="Repair guides" icon={<Activity size={16} />}>
          {detail.guides.map((guide) => (
            <div key={guide.id} className="list-item">
              <strong>{guide.title}</strong>
              <span>{guide.summary}</span>
            </div>
          ))}
        </ContentPanel>
        <ContentPanel title="Parts" icon={<Layers3 size={16} />}>
          {detail.parts.map((part) => (
            <div key={part.id} className="list-item">
              <strong>{part.name}</strong>
              <span>{part.vendor} · ${part.price.toFixed(2)}</span>
            </div>
          ))}
        </ContentPanel>
        <ContentPanel title="Tools and venues" icon={<Wrench size={16} />}>
          {detail.tools.slice(0, 2).map((tool) => (
            <div key={tool.id} className="list-item">
              <strong>{tool.name}</strong>
              <span>{tool.purpose}</span>
            </div>
          ))}
          {detail.venues.slice(0, 2).map((venue) => (
            <div key={venue.id} className="list-item">
              <strong>{venue.name}</strong>
              <span>{venue.city} · {venue.rating.toFixed(1)} rating</span>
            </div>
          ))}
        </ContentPanel>
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <span className="eyebrow"><Sparkles size={14} /> Graph view</span>
            <h2>How the repair path connects</h2>
          </div>
        </div>
        <GraphCanvas graph={graph} />
      </section>

      <section className="section-card">
        <div className="section-heading">
          <div>
            <span className="eyebrow"><Layers3 size={14} /> Related devices</span>
            <h2>Devices linked through the graph</h2>
          </div>
        </div>
        <div className="device-grid">
          {related.length ? related.map((device) => <DeviceCard key={device.id} device={device} />) : <div className="placeholder">No related devices found yet.</div>}
        </div>
      </section>
    </section>
  );
}

function ExplorePage() {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <span className="eyebrow"><Database size={14} /> Queries</span>
          <h2>Why CognoDB helps here</h2>
        </div>
      </div>
      <p className="muted">
        This app is built around traversals, not tables. The important questions are relationship questions, so the graph stays readable and flexible.
      </p>
      <div className="query-grid">
        <QueryCard title="Device to repair path" text="Device -> Symptom -> Cause -> RepairGuide -> Part -> Tool -> Venue" />
        <QueryCard title="Related devices" text="Find sibling devices through shared symptoms and guide chains." />
        <QueryCard title="Relationally awkward query" text="Trace a symptom, guide, part, and venue chain across several hops." />
      </div>
    </section>
  );
}

function AboutPage() {
  return (
    <section className="section-card">
      <div className="section-heading">
        <div>
          <span className="eyebrow"><Sparkles size={14} /> Assignment notes</span>
          <h2>What’s included</h2>
        </div>
      </div>
      <ul className="bullet-list">
        <li>Backend API with graceful demo-mode fallback</li>
        <li>Parameterized Cypher examples</li>
        <li>Seed generator for a connected graph</li>
        <li>Readable UI with loading, empty, and error states</li>
      </ul>
    </section>
  );
}

function ContentPanel({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <div className="panel">
      <div className="panel-title">
        <span>{icon}</span>
        <strong>{title}</strong>
      </div>
      <div className="panel-body">{children}</div>
    </div>
  );
}

function StatCard({ label, value, description }: Insight) {
  return (
    <div className="stat-card">
      <strong>{value}</strong>
      <span>{label}</span>
      <small>{description}</small>
    </div>
  );
}

function QueryCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="query-card">
      <strong>{title}</strong>
      <p>{text}</p>
    </div>
  );
}

function GraphPreview() {
  return (
    <svg viewBox="0 0 420 240" className="graph-svg" aria-hidden="true">
      <defs>
        <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
      <path d="M90 160 C 150 120, 210 100, 270 84" stroke="url(#lineGrad)" strokeWidth="3" fill="none" />
      <path d="M90 160 C 155 170, 215 180, 285 160" stroke="#93c5fd" strokeWidth="3" fill="none" />
      <circle cx="90" cy="160" r="16" className="node device" />
      <circle cx="270" cy="84" r="16" className="node symptom" />
      <circle cx="285" cy="160" r="16" className="node guide" />
      <circle cx="350" cy="200" r="16" className="node part" />
      <circle cx="350" cy="48" r="16" className="node tool" />
      <text x="72" y="198">Device</text>
      <text x="250" y="56">Symptom</text>
      <text x="247" y="197">Guide</text>
      <text x="332" y="236">Part</text>
      <text x="332" y="28">Tool</text>
    </svg>
  );
}

function GraphCanvas({ graph }: { graph: GraphResponse | null }) {
  if (!graph) {
    return <div className="placeholder">Loading graph...</div>;
  }
  return (
    <div className="graph-canvas">
      <svg viewBox="0 0 1200 520" className="graph-full">
        {graph.edges.map((edge) => {
          const source = graph.nodes.find((node) => node.id === edge.source);
          const target = graph.nodes.find((node) => node.id === edge.target);
          if (!source || !target) return null;
          return <line key={edge.id} x1={source.x} y1={source.y} x2={target.x} y2={target.y} className="graph-edge" />;
        })}
        {graph.nodes.map((node) => (
          <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
            <circle r="26" className={`graph-node ${node.group}`} />
            <text textAnchor="middle" y="55" className="graph-label">
              {node.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export default App;
