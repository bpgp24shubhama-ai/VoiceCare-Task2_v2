"""
HTML Dashboard Generator.

Reads all JSON outputs from data/output/ and data/reports/,
then generates a single self-contained HTML dashboard file.
"""

import glob
import json
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def _data_base() -> str:
    """Return the root directory used for all data I/O.

    Reads the VOICECARE_DATA_DIR environment variable so that Vercel
    deployments (read-only /var/task filesystem) can redirect to /tmp/.
    Falls back to the project root relative to this file.
    """
    custom = os.environ.get("VOICECARE_DATA_DIR")
    if custom:
        return custom
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


_BASE = _data_base()
OUTPUT_DIR = os.path.join(_BASE, "data", "output")
REPORTS_DIR = os.path.join(_BASE, "data", "reports")
DASHBOARD_PATH = os.path.join(_BASE, "data", "dashboard.html")


# ── Data loading ─────────────────────────────────────────────────────────────

def _load_latest(pattern: str, base_dir: str) -> Optional[dict]:
    matches = sorted(glob.glob(os.path.join(base_dir, pattern)))
    if not matches:
        return None
    try:
        with open(matches[-1], encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Could not load %s: %s", matches[-1], exc)
        return None


def _load_all(pattern: str, base_dir: str) -> list:
    out = []
    for path in sorted(glob.glob(os.path.join(base_dir, pattern))):
        try:
            with open(path, encoding="utf-8") as f:
                out.append((os.path.basename(path), json.load(f)))
        except Exception as exc:
            logger.warning("Could not load %s: %s", path, exc)
    return out


def _collect() -> dict:
    return {
        "competitive_analysis": _load_latest("competitive_analysis_*.json", OUTPUT_DIR),
        "geo_audit":            _load_latest("geo_audit_*.json", OUTPUT_DIR),
        "growth_playbook":      _load_latest("growth_playbook_*.json", OUTPUT_DIR),
        "algorithm_guide":      _load_latest("algorithm_guide_*.json", OUTPUT_DIR),
        "content_calendar":     _load_latest("week*_calendar_*.json", OUTPUT_DIR),
        "viral_loops":          _load_latest("viral_loops_*.json", OUTPUT_DIR),
        "employee_advocacy":    _load_latest("employee_advocacy_*.json", OUTPUT_DIR),
        "partnerships":         _load_latest("partnerships_*.json", OUTPUT_DIR),
        "geo_content_plan":     _load_latest("geo_content_plan_*.json", OUTPUT_DIR),
        "ai_mentions":          _load_latest("ai_mentions_*.json", OUTPUT_DIR),
        "schema_recs":          _load_latest("schema_recommendations_*.json", OUTPUT_DIR),
        "weekly_reports":       _load_all("week_*_report.json", REPORTS_DIR),
        "generated_content":    _load_all("content_*.json", OUTPUT_DIR),
        "generated_at":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── Public entry point ────────────────────────────────────────────────────────

def generate_dashboard(output_path: Optional[str] = None) -> str:
    """Read all JSON outputs and write a combined HTML dashboard.

    Returns the path to the generated HTML file.
    """
    data = _collect()
    html = _build_html(data)
    path = output_path or DASHBOARD_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Dashboard saved → %s", path)
    return path


# ── HTML builder ──────────────────────────────────────────────────────────────

def _build_html(data: dict) -> str:
    # Embed JSON safely inside a <script> block (escape </script> sequences)
    data_json = json.dumps(data, default=str, ensure_ascii=False).replace("</", "<\\/")
    generated_at = data.get("generated_at", "")
    return _TEMPLATE.replace("/*__DATA__*/null", data_json).replace("__GENERATED_AT__", generated_at)


# ── HTML template ─────────────────────────────────────────────────────────────
# Note: this is a plain Python string (not an f-string) so JS {} are safe.

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>VoiceCare.ai — Growth Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body{background:#0f172a;color:#e2e8f0;font-family:system-ui,sans-serif;margin:0}
  .sidebar{width:220px;min-height:100vh;background:#1e293b;border-right:1px solid #334155;position:fixed;top:0;left:0;overflow-y:auto}
  .main{margin-left:220px;padding:28px;min-height:100vh}
  .nav-link{display:flex;align-items:center;gap:10px;padding:9px 14px;border-radius:8px;cursor:pointer;color:#94a3b8;font-size:.85rem;transition:all .15s;text-decoration:none;margin:2px 8px}
  .nav-link:hover,.nav-link.active{background:#6366f1;color:#fff}
  .section{display:none}.section.active{display:block}
  .card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;margin-bottom:0}
  .stat-card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px;text-align:center}
  .progress-bar{height:8px;background:#334155;border-radius:4px;overflow:hidden}
  .progress-fill{height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:4px;transition:width 1s ease}
  table{width:100%;border-collapse:collapse}
  th{text-align:left;padding:8px 12px;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:#64748b;border-bottom:1px solid #334155}
  td{padding:10px 12px;border-bottom:1px solid #1e293b40;font-size:.85rem;vertical-align:top}
  tr:hover td{background:#ffffff06}
  .chip{display:inline-block;padding:2px 9px;border-radius:9999px;font-size:.7rem;font-weight:600;margin:2px}
  .chip-purple{background:#4f46e520;color:#a5b4fc;border:1px solid #4f46e540}
  .chip-green{background:#16a34a20;color:#86efac;border:1px solid #16a34a40}
  .chip-amber{background:#d9770620;color:#fcd34d;border:1px solid #d9770640}
  .chip-red{background:#dc262620;color:#fca5a5;border:1px solid #dc262640}
  .badge-high{background:#fef2f2;color:#dc2626;padding:2px 8px;border-radius:9999px;font-size:.7rem;font-weight:700}
  .badge-medium{background:#fffbeb;color:#d97706;padding:2px 8px;border-radius:9999px;font-size:.7rem;font-weight:700}
  .badge-low{background:#f0fdf4;color:#16a34a;padding:2px 8px;border-radius:9999px;font-size:.7rem;font-weight:700}
  ::-webkit-scrollbar{width:5px}
  ::-webkit-scrollbar-track{background:#0f172a}
  ::-webkit-scrollbar-thumb{background:#334155;border-radius:3px}
  h1{font-size:1.6rem;font-weight:700;color:#f8fafc;margin-bottom:20px}
  h3{font-size:1rem;font-weight:600;color:#cbd5e1;margin-bottom:12px}
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar p-4">
  <div style="padding:8px 6px 20px">
    <div style="color:#818cf8;font-weight:700;font-size:1.1rem">VoiceCare.ai</div>
    <div style="color:#475569;font-size:.75rem">Growth Dashboard</div>
    <div style="color:#334155;font-size:.7rem;margin-top:4px">__GENERATED_AT__</div>
  </div>
  <a class="nav-link active" onclick="show('overview',this)">📊 Overview</a>
  <a class="nav-link" onclick="show('competitive',this)">🏆 Competitive</a>
  <a class="nav-link" onclick="show('geo',this)">🔍 GEO Audit</a>
  <a class="nav-link" onclick="show('playbook',this)">🚀 Growth Playbook</a>
  <a class="nav-link" onclick="show('calendar',this)">📅 Content Calendar</a>
  <a class="nav-link" onclick="show('algorithm',this)">⚡ LinkedIn Algorithm</a>
  <a class="nav-link" onclick="show('hacks',this)">🎯 Growth Hacks</a>
  <a class="nav-link" onclick="show('reports',this)">📈 Weekly Reports</a>
  <a class="nav-link" onclick="show('content',this)">✍️ Generated Content</a>
</aside>

<!-- Main content -->
<main class="main">

  <!-- OVERVIEW -->
  <div id="overview" class="section active">
    <h1>Dashboard Overview</h1>
    <div id="overview-stats" class="grid grid-cols-4 gap-4 mb-6"></div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3>Follower Progress to 10,000</h3>
        <div id="follower-progress"></div>
      </div>
      <div class="card">
        <h3>Competitor GEO Scores</h3>
        <canvas id="geo-chart-overview"></canvas>
      </div>
    </div>
    <div class="card">
      <h3>Available Reports</h3>
      <div id="report-availability" class="grid grid-cols-4 gap-3"></div>
    </div>
  </div>

  <!-- COMPETITIVE ANALYSIS -->
  <div id="competitive" class="section">
    <h1>Competitive Analysis</h1>
    <div id="comp-stats" class="grid grid-cols-3 gap-4 mb-6"></div>
    <div class="card mb-6">
      <h3>Competitor Organic Traffic vs AI Visibility</h3>
      <canvas id="comp-chart" height="140"></canvas>
    </div>
    <div class="card mb-6" style="overflow-x:auto">
      <h3>Competitor Details</h3>
      <table>
        <thead><tr>
          <th>Company</th><th>Organic Traffic</th><th>Keywords</th>
          <th>Authority</th><th>AI Visibility</th><th>LinkedIn Est.</th><th>Engagement</th>
        </tr></thead>
        <tbody id="comp-tbody"></tbody>
      </table>
    </div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="card"><h3>Keyword Gaps</h3><ul id="keyword-gaps" class="space-y-2 text-sm" style="color:#94a3b8"></ul></div>
      <div class="card"><h3>Content Opportunities</h3><ul id="content-opps" class="space-y-2 text-sm" style="color:#94a3b8"></ul></div>
    </div>
    <div class="card">
      <h3>Quick Win Strategies</h3>
      <ul id="quick-wins" class="space-y-2 text-sm" style="color:#94a3b8"></ul>
    </div>
  </div>

  <!-- GEO AUDIT -->
  <div id="geo" class="section">
    <h1>GEO Audit (AI Engine Visibility)</h1>
    <div id="geo-stats" class="grid grid-cols-4 gap-4 mb-6"></div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3>Digital Footprint</h3>
        <div id="geo-footprint"></div>
      </div>
      <div class="card">
        <h3>Competitor GEO Rankings</h3>
        <div id="geo-comp-list"></div>
      </div>
    </div>
    <div class="card mb-6" style="overflow-x:auto">
      <h3>Query Analysis</h3>
      <table>
        <thead><tr><th>Query</th><th>AI Cites</th><th>VoiceCare Mentioned</th><th>Gap to Close</th></tr></thead>
        <tbody id="geo-queries"></tbody>
      </table>
    </div>
    <div class="card">
      <h3>Prioritised GEO Action Plan</h3>
      <div id="geo-actions" class="space-y-3"></div>
    </div>
  </div>

  <!-- GROWTH PLAYBOOK -->
  <div id="playbook" class="section">
    <h1>12-Week Growth Playbook</h1>
    <div id="phases" class="grid grid-cols-3 gap-4 mb-6"></div>
    <div class="card mb-6">
      <h3>Weekly Follower Gain Projection</h3>
      <canvas id="playbook-chart" height="120"></canvas>
    </div>
    <div id="weekly-plans" class="space-y-3"></div>
  </div>

  <!-- CONTENT CALENDAR -->
  <div id="calendar" class="section">
    <h1>Content Calendar</h1>
    <div id="cal-header" class="card mb-6"></div>
    <div id="cal-posts" class="space-y-4"></div>
    <div id="cal-tasks" class="card mt-6" style="display:none">
      <h3>Weekly Engagement Tasks</h3>
      <ul id="cal-task-list" class="space-y-2 text-sm" style="color:#94a3b8"></ul>
    </div>
  </div>

  <!-- LINKEDIN ALGORITHM -->
  <div id="algorithm" class="section">
    <h1>LinkedIn Algorithm Guide</h1>
    <div id="algo-posting" class="grid grid-cols-4 gap-4 mb-6"></div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3 style="color:#4ade80">✅ What's Working</h3>
        <div id="algo-working" class="space-y-3"></div>
      </div>
      <div class="card">
        <h3 style="color:#f87171">❌ What to Avoid</h3>
        <div id="algo-avoid" class="space-y-3"></div>
      </div>
    </div>
    <div class="card">
      <h3>Algorithm Updates</h3>
      <div id="algo-updates" class="space-y-3"></div>
    </div>
  </div>

  <!-- GROWTH HACKS -->
  <div id="hacks" class="section">
    <h1>Growth Hacks</h1>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="card">
        <h3 style="color:#818cf8">🔄 Viral Content Loops</h3>
        <div id="viral-loops" class="space-y-3"></div>
      </div>
      <div class="card">
        <h3 style="color:#818cf8">🤝 Partnerships</h3>
        <div id="partnerships" class="space-y-3"></div>
      </div>
    </div>
    <div class="card mb-6">
      <h3 style="color:#818cf8">📢 Employee Advocacy Program</h3>
      <div id="advocacy" class="grid grid-cols-3 gap-4"></div>
    </div>
    <div class="card" id="geo-plan-card" style="display:none">
      <h3 style="color:#818cf8">📝 GEO Content Plan</h3>
      <div id="geo-plan-list" class="space-y-3"></div>
    </div>
  </div>

  <!-- WEEKLY REPORTS -->
  <div id="reports" class="section">
    <h1>Weekly Reports</h1>
    <div class="card mb-6">
      <h3>Follower Growth Over Time</h3>
      <canvas id="growth-chart" height="120"></canvas>
    </div>
    <div id="reports-list" class="space-y-4"></div>
  </div>

  <!-- GENERATED CONTENT -->
  <div id="content" class="section">
    <h1>Generated Content</h1>
    <div id="content-list" class="space-y-4"></div>
  </div>

</main>

<script>
const DATA = /*__DATA__*/null;

// ── Navigation ───────────────────────────────────────────────────────────────
function show(id, el) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (el) el.classList.add('active');
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function badge(val) {
  if (!val) return '';
  const v = String(val).toLowerCase();
  if (v === 'high') return '<span class="badge-high">HIGH</span>';
  if (v === 'medium' || v === 'med') return '<span class="badge-medium">MED</span>';
  if (v === 'low') return '<span class="badge-low">LOW</span>';
  return '';
}
function listHtml(arr) {
  if (!arr || !arr.length) return '<li style="color:#475569;font-size:.8rem">No data available.</li>';
  return arr.map(i => '<li style="padding:3px 0">• ' + esc(i) + '</li>').join('');
}
function statCard(icon, label, value, sub) {
  return '<div class="stat-card"><div style="font-size:1.6rem;margin-bottom:6px">' + icon +
    '</div><div style="font-size:1.5rem;font-weight:700;color:#f8fafc">' + esc(value) +
    '</div><div style="font-size:.72rem;color:#64748b;margin-top:4px">' + esc(label) +
    '</div>' + (sub ? '<div style="font-size:.72rem;color:#818cf8;margin-top:2px">' + esc(sub) + '</div>' : '') +
    '</div>';
}
function noData(section, cmd) {
  return '<div class="card" style="text-align:center;padding:40px;color:#475569">No ' +
    section + ' data available yet.<br><code style="color:#818cf8;font-size:.8rem">' + esc(cmd) + '</code></div>';
}

// ── OVERVIEW ─────────────────────────────────────────────────────────────────
function buildOverview() {
  const geo  = DATA.geo_audit || {};
  const comp = DATA.competitive_analysis || {};
  const rpts = DATA.weekly_reports || [];

  const available = ['competitive_analysis','geo_audit','growth_playbook','algorithm_guide',
    'content_calendar','viral_loops','employee_advocacy','partnerships',
    'geo_content_plan','ai_mentions','schema_recs']
    .filter(k => DATA[k]).length + rpts.length + (DATA.generated_content||[]).length;

  document.getElementById('overview-stats').innerHTML = [
    statCard('📁', 'Total JSON Reports', available),
    statCard('🔍', 'GEO Visibility Score', geo.current_visibility_score ? geo.current_visibility_score + '/100' : '–'),
    statCard('🏆', 'Competitors Tracked', (comp.competitors||[]).length || '–'),
    statCard('🎯', 'GEO Actions Planned', (geo.geo_action_plan||[]).length || '–'),
  ].join('');

  // Follower progress
  const start = 2900, target = 10000;
  const latestRpt = rpts.length ? rpts[rpts.length-1][1] : null;
  const current = (latestRpt && latestRpt.metrics && latestRpt.metrics.current_followers) || start;
  const pct = Math.min(100, Math.round((current - start) / (target - start) * 100));
  document.getElementById('follower-progress').innerHTML =
    '<div style="display:flex;justify-content:space-between;font-size:.8rem;color:#64748b;margin-bottom:8px">' +
      '<span>Start: ' + start.toLocaleString() + '</span>' +
      '<span>Current: <b style="color:#f8fafc">' + current.toLocaleString() + '</b></span>' +
      '<span>Target: ' + target.toLocaleString() + '</span>' +
    '</div>' +
    '<div class="progress-bar"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
    '<div style="text-align:right;font-size:.72rem;color:#818cf8;margin-top:4px">' + pct + '% of goal</div>' +
    '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;text-align:center">' +
      '<div><div style="font-size:1.2rem;font-weight:700;color:#f8fafc">' + (current-start).toLocaleString() + '</div><div style="font-size:.7rem;color:#64748b">Gained</div></div>' +
      '<div><div style="font-size:1.2rem;font-weight:700;color:#f8fafc">' + (target-current).toLocaleString() + '</div><div style="font-size:.7rem;color:#64748b">Remaining</div></div>' +
      '<div><div style="font-size:1.2rem;font-weight:700;color:#818cf8">' + pct + '%</div><div style="font-size:.7rem;color:#64748b">Complete</div></div>' +
    '</div>';

  // GEO competitor chart
  const geoComps = (geo.competitor_comparison||[]).slice(0,8);
  if (geoComps.length) {
    const ctx = document.getElementById('geo-chart-overview').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: geoComps.map(c => c.company||''),
        datasets: [{ label: 'GEO Score', data: geoComps.map(c => c.geo_score||0),
          backgroundColor: geoComps.map(c => (c.company||'').toLowerCase().includes('voicecare') ? '#6366f1' : '#334155'),
          borderRadius: 5 }]
      },
      options: { plugins: { legend: { display: false } },
        scales: { x: { ticks: { color: '#64748b' }, grid: { display: false } },
                  y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' }, max: 100 } } }
    });
  } else {
    document.getElementById('geo-chart-overview').parentElement.innerHTML +=
      '<p style="color:#475569;font-size:.8rem;text-align:center;margin-top:12px">Run <code style="color:#818cf8">python run.py geo</code> to populate.</p>';
  }

  // Availability grid
  const allItems = [
    {k:'competitive_analysis',l:'Competitive Analysis',i:'🏆'},
    {k:'geo_audit',l:'GEO Audit',i:'🔍'},
    {k:'growth_playbook',l:'Growth Playbook',i:'🚀'},
    {k:'algorithm_guide',l:'Algorithm Guide',i:'⚡'},
    {k:'content_calendar',l:'Content Calendar',i:'📅'},
    {k:'viral_loops',l:'Viral Loops',i:'🔄'},
    {k:'employee_advocacy',l:'Employee Advocacy',i:'📢'},
    {k:'partnerships',l:'Partnerships',i:'🤝'},
    {k:'geo_content_plan',l:'GEO Content Plan',i:'📝'},
    {k:'ai_mentions',l:'AI Mentions',i:'🤖'},
    {k:'schema_recs',l:'Schema Recs',i:'🗂️'},
  ];
  document.getElementById('report-availability').innerHTML =
    allItems.map(({k,l,i}) => {
      const has = !!DATA[k];
      return '<div style="display:flex;align-items:center;gap:8px;padding:10px;border-radius:8px;' +
        (has ? 'background:#4f46e510;border:1px solid #4f46e530' : 'background:#1e293b;border:1px solid #1e293b;opacity:.4') + '">' +
        '<span style="font-size:1.1rem">' + i + '</span>' +
        '<span style="font-size:.78rem;color:' + (has ? '#c7d2fe' : '#475569') + '">' + l + '</span>' +
        (has ? '<span style="margin-left:auto;color:#4ade80;font-size:.75rem">✓</span>' : '<span style="margin-left:auto;color:#334155;font-size:.75rem">–</span>') +
        '</div>';
    }).join('') +
    rpts.map(([fn]) =>
      '<div style="display:flex;align-items:center;gap:8px;padding:10px;border-radius:8px;background:#4f46e510;border:1px solid #4f46e530">' +
        '<span style="font-size:1.1rem">📈</span>' +
        '<span style="font-size:.78rem;color:#c7d2fe">' + esc(fn.replace('.json','')) + '</span>' +
        '<span style="margin-left:auto;color:#4ade80;font-size:.75rem">✓</span>' +
      '</div>'
    ).join('');
}

// ── COMPETITIVE ───────────────────────────────────────────────────────────────
function buildCompetitive() {
  const data = DATA.competitive_analysis;
  const section = document.getElementById('competitive');
  if (!data) { section.innerHTML = '<h1>Competitive Analysis</h1>' + noData('competitive analysis','python run.py strategy'); return; }

  const competitors = data.competitors || [];
  document.getElementById('comp-stats').innerHTML = [
    statCard('🏢','Competitors Analysed', competitors.length),
    statCard('🔑','Keyword Gaps Found', (data.keyword_gap||[]).length),
    statCard('💡','Content Opportunities', (data.content_opportunities||[]).length),
  ].join('');

  if (competitors.length) {
    const ctx = document.getElementById('comp-chart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: competitors.map(c => c.name||''),
        datasets: [
          { label: 'Organic Traffic', data: competitors.map(c => parseInt(c.organic_traffic)||0), backgroundColor: '#6366f1', borderRadius: 4 },
          { label: 'AI Visibility (×1000)', data: competitors.map(c => (parseFloat(c.ai_visibility_score)||0)*1000), backgroundColor: '#8b5cf6', borderRadius: 4 },
        ]
      },
      options: { plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: { x: { ticks: { color: '#64748b' }, grid: { display: false } },
                  y: { ticks: { color: '#64748b' }, grid: { color: '#334155' } } } }
    });
  }

  document.getElementById('comp-tbody').innerHTML = competitors.map(c =>
    '<tr><td style="color:#f8fafc;font-weight:600">' + esc(c.name) + '</td>' +
    '<td>' + esc(c.organic_traffic) + '</td><td>' + esc(c.organic_keywords) + '</td>' +
    '<td>' + esc(c.authority_score) + '</td>' +
    '<td><span class="chip chip-purple">' + esc(c.ai_visibility_score) + '/10</span></td>' +
    '<td>' + esc(c.linkedin_followers_estimate) + '</td>' +
    '<td><span class="chip chip-amber">' + esc(c.engagement_level) + '</span></td></tr>'
  ).join('');

  document.getElementById('keyword-gaps').innerHTML = listHtml(data.keyword_gap);
  document.getElementById('content-opps').innerHTML = listHtml(data.content_opportunities);
  document.getElementById('quick-wins').innerHTML = listHtml(data.quick_win_strategies);
}

// ── GEO AUDIT ─────────────────────────────────────────────────────────────────
function buildGeo() {
  const data = DATA.geo_audit;
  const section = document.getElementById('geo');
  if (!data) { section.innerHTML = '<h1>GEO Audit</h1>' + noData('GEO audit','python run.py geo'); return; }

  const fp = data.digital_footprint || {};
  const actions = (data.geo_action_plan||[]).slice().sort((a,b) => (a.priority||99)-(b.priority||99));

  document.getElementById('geo-stats').innerHTML = [
    statCard('📊','Visibility Score', (data.current_visibility_score||0)+'/100'),
    statCard('🌐','Website Authority', fp.website_authority||'–'),
    statCard('📋','Review Platforms', (fp.review_site_presence||[]).length),
    statCard('🎯','Action Items', actions.length),
  ].join('');

  document.getElementById('geo-footprint').innerHTML =
    '<div style="font-size:.85rem;color:#94a3b8;line-height:1.8">' +
    '<b style="color:#94a3b8">Knowledge Base:</b> ' + esc(fp.knowledge_base_status||'–') + '<br>' +
    '<b style="color:#94a3b8">Publications:</b><br>' +
    (fp.publication_mentions||[]).map(p => '<span class="chip chip-green">' + esc(p) + '</span>').join('') +
    '<br><br><b style="color:#94a3b8">Review Sites:</b><br>' +
    (fp.review_site_presence||[]).map(p => '<span class="chip chip-purple">' + esc(p) + '</span>').join('') +
    '</div>';

  document.getElementById('geo-comp-list').innerHTML = (data.competitor_comparison||[]).map(c =>
    '<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #334155">' +
    '<div style="flex:1;font-size:.85rem;color:#e2e8f0">' + esc(c.company) + '</div>' +
    '<div class="progress-bar" style="width:80px"><div class="progress-fill" style="width:' + Math.min(100,c.geo_score||0) + '%"></div></div>' +
    '<div style="font-size:.85rem;font-weight:700;color:#818cf8;width:36px;text-align:right">' + (c.geo_score||0) + '</div>' +
    '</div>'
  ).join('') || '<p style="color:#475569;font-size:.8rem">No competitor data.</p>';

  document.getElementById('geo-queries').innerHTML = (data.query_analysis||[]).map(q =>
    '<tr><td style="color:#a5b4fc;font-size:.8rem">"' + esc(q.query) + '"</td>' +
    '<td>' + (q.likely_ai_response_includes||[]).slice(0,3).map(s => '<span class="chip chip-purple">' + esc(s) + '</span>').join('') + '</td>' +
    '<td><span class="chip ' + (q.voicecare_mentioned ? 'chip-green' : 'chip-red') + '">' + (q.voicecare_mentioned ? '✓ Yes' : '✗ No') + '</span></td>' +
    '<td style="font-size:.78rem;color:#94a3b8">' + esc(q.gap_to_close) + '</td></tr>'
  ).join('');

  document.getElementById('geo-actions').innerHTML = actions.map(a =>
    '<div style="display:flex;gap:14px;padding:14px;background:#0f172a;border-radius:10px;border:1px solid #334155">' +
      '<div style="flex-shrink:0;width:30px;height:30px;border-radius:50%;background:#6366f1;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;color:#fff">' + (a.priority||'–') + '</div>' +
      '<div style="flex:1">' +
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">' +
          '<span style="font-weight:600;color:#f8fafc;font-size:.9rem">' + esc(a.action) + '</span>' +
          badge(a.expected_impact) +
        '</div>' +
        '<div style="display:flex;gap:14px;font-size:.75rem;color:#64748b">' +
          '<span>📁 ' + esc(a.category) + '</span>' +
          '<span>⏱ ' + esc(a.timeline) + '</span>' +
          '<span>Effort: ' + esc(a.effort) + '</span>' +
        '</div>' +
        (a.details ? '<div style="font-size:.78rem;color:#64748b;margin-top:6px">' + esc(a.details) + '</div>' : '') +
      '</div>' +
    '</div>'
  ).join('') || '<p style="color:#475569">No action items found.</p>';
}

// ── GROWTH PLAYBOOK ───────────────────────────────────────────────────────────
function buildPlaybook() {
  const data = DATA.growth_playbook;
  const section = document.getElementById('playbook');
  if (!data) { section.innerHTML = '<h1>Growth Playbook</h1>' + noData('growth playbook','python run.py growth-hacks'); return; }

  const phaseColors = ['#6366f1','#8b5cf6','#a855f7'];
  const phases = data.phases || [];
  document.getElementById('phases').innerHTML = phases.map((p,i) =>
    '<div class="card" style="border-top:3px solid ' + phaseColors[i] + '">' +
      '<div style="font-size:.72rem;color:#64748b;margin-bottom:4px">Phase ' + (p.phase||i+1) + ' · Weeks ' + esc(p.weeks) + '</div>' +
      '<div style="font-size:1rem;font-weight:700;color:#f8fafc;margin-bottom:4px">' + esc(p.name) + '</div>' +
      '<div style="font-size:1.4rem;font-weight:700;color:#818cf8;margin-bottom:10px">' + ((p.target_followers||0).toLocaleString()) + ' followers</div>' +
      '<ul style="font-size:.75rem;color:#64748b;line-height:1.8">' +
      (p.key_strategies||[]).slice(0,4).map(s => '<li>• ' + esc(s) + '</li>').join('') +
      '</ul></div>'
  ).join('');

  const allWeeks = phases.flatMap(p => p.weekly_plans||[]);
  if (allWeeks.length) {
    const ctx = document.getElementById('playbook-chart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: allWeeks.map(w => 'Wk' + w.week),
        datasets: [
          { label: 'Follower Gain', data: allWeeks.map(w => w.expected_follower_gain||0),
            borderColor: '#6366f1', backgroundColor: '#6366f130', fill: true, tension: 0.4, pointRadius: 3 },
          { label: 'Comments to Make', data: allWeeks.map(w => (w.engagement_targets||{}).comments_to_make||0),
            borderColor: '#8b5cf6', borderDash: [4,4], fill: false, tension: 0.4, pointRadius: 3 },
        ]
      },
      options: { plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: { x: { ticks: { color: '#64748b' }, grid: { display: false } },
                  y: { ticks: { color: '#64748b' }, grid: { color: '#334155' } } } }
    });
  }

  document.getElementById('weekly-plans').innerHTML = allWeeks.map(w =>
    '<div class="card" style="display:flex;gap:14px;align-items:flex-start">' +
      '<div style="flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#6366f1;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;color:#fff">W' + (w.week||'?') + '</div>' +
      '<div style="flex:1">' +
        '<div style="font-weight:600;color:#f8fafc;margin-bottom:2px">' + esc(w.primary_hack) + '</div>' +
        '<div style="font-size:.75rem;color:#64748b;margin-bottom:6px">' + (w.posts_count||0) + ' posts · +' + (w.expected_follower_gain||0) + ' followers expected</div>' +
        '<div>' + (w.post_types||[]).map(t => '<span class="chip chip-purple">' + esc(t) + '</span>').join('') + '</div>' +
      '</div>' +
      '<div style="display:flex;gap:12px;font-size:.75rem;color:#94a3b8">' +
        '<span>💬 ' + ((w.engagement_targets||{}).comments_to_make||0) + '</span>' +
        '<span>🔗 ' + ((w.engagement_targets||{}).connections_to_send||0) + '</span>' +
      '</div>' +
    '</div>'
  ).join('');
}

// ── CONTENT CALENDAR ──────────────────────────────────────────────────────────
function buildCalendar() {
  const data = DATA.content_calendar;
  const section = document.getElementById('calendar');
  if (!data) { section.innerHTML = '<h1>Content Calendar</h1>' + noData('calendar','python run.py calendar 1'); return; }

  document.getElementById('cal-header').innerHTML =
    '<div style="display:flex;align-items:center;gap:28px">' +
      '<div><div style="color:#64748b;font-size:.72rem;text-transform:uppercase">Week</div><div style="font-size:2rem;font-weight:700;color:#f8fafc">' + (data.week_number||'?') + '</div></div>' +
      '<div><div style="color:#64748b;font-size:.72rem;text-transform:uppercase">Theme</div><div style="font-size:1rem;font-weight:600;color:#a5b4fc">' + esc(data.theme) + '</div></div>' +
      '<div style="margin-left:auto"><div style="color:#64748b;font-size:.72rem;text-transform:uppercase">Follower Milestone</div><div style="font-size:1.5rem;font-weight:700;color:#4ade80">' + ((data.follower_milestone||0).toLocaleString()) + '</div></div>' +
    '</div>';

  document.getElementById('cal-posts').innerHTML = (data.posts||[]).map(p =>
    '<div class="card">' +
      '<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:12px">' +
        '<div style="flex-shrink:0;width:72px;text-align:center">' +
          '<div style="font-weight:700;color:#818cf8;font-size:.9rem">' + esc(p.day) + '</div>' +
          '<div style="font-size:.7rem;color:#64748b">' + esc(p.post_time) + '</div>' +
        '</div>' +
        '<div style="flex:1">' +
          '<div style="margin-bottom:6px">' +
            '<span class="chip chip-purple">' + esc(p.post_type) + '</span>' +
            (p.expected_reach_multiplier ? '<span class="chip chip-green">📈 ' + esc(p.expected_reach_multiplier) + '</span>' : '') +
          '</div>' +
          '<div style="font-weight:600;color:#f8fafc;font-size:.9rem">' + esc(p.hook) + '</div>' +
        '</div>' +
      '</div>' +
      '<div style="background:#0f172a;border-radius:8px;padding:12px;font-size:.78rem;color:#94a3b8;white-space:pre-wrap;margin-bottom:10px;max-height:140px;overflow:hidden">' +
        esc((p.full_post_text||'').slice(0,600)) + ((p.full_post_text||'').length>600?'\n…':'') +
      '</div>' +
      '<div style="margin-bottom:8px">' + (p.hashtags||[]).slice(0,8).map(h => '<span class="chip chip-amber">' + esc(h) + '</span>').join('') + '</div>' +
      '<div style="font-size:.75rem;color:#64748b">📎 ' + esc(p.media_suggestion) + ' &nbsp;|&nbsp; 💬 ' + esc(p.engagement_strategy) + '</div>' +
    '</div>'
  ).join('');

  const tasks = data.weekly_engagement_tasks||[];
  if (tasks.length) {
    document.getElementById('cal-tasks').style.display = '';
    document.getElementById('cal-task-list').innerHTML = listHtml(tasks);
  }
}

// ── ALGORITHM ─────────────────────────────────────────────────────────────────
function buildAlgorithm() {
  const data = DATA.algorithm_guide;
  const section = document.getElementById('algorithm');
  if (!data) { section.innerHTML = '<h1>LinkedIn Algorithm Guide</h1>' + noData('algorithm guide','python run.py strategy'); return; }

  const ps = data.optimal_posting_strategy || {};
  const formats = (ps.formats_ranked||[]).slice(0,3).join(', ');
  document.getElementById('algo-posting').innerHTML = [
    statCard('⏰','Best Times', (ps.times||[]).join(', ')||'–'),
    statCard('📊','Frequency', ps.frequency||'–'),
    statCard('#️⃣','Hashtags', ps.hashtag_count||'–'),
    statCard('📏','Post Length', ps.post_length||'–'),
  ].join('');

  document.getElementById('algo-working').innerHTML = (data.whats_working||[]).map(w =>
    '<div style="background:#052e16;border:1px solid #166534;border-radius:8px;padding:12px">' +
      '<div style="font-weight:600;color:#4ade80;font-size:.85rem;margin-bottom:4px">' + esc(w.tactic) + '</div>' +
      '<div style="font-size:.78rem;color:#94a3b8">' + esc(w.why) + '</div>' +
      (w.data ? '<div style="font-size:.75rem;color:#86efac;margin-top:4px">📊 ' + esc(w.data) + '</div>' : '') +
    '</div>'
  ).join('') || '<p style="color:#475569;font-size:.8rem">No data.</p>';

  document.getElementById('algo-avoid').innerHTML = (data.what_to_avoid||[]).map(w =>
    '<div style="background:#2d0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:12px">' +
      '<div style="font-weight:600;color:#f87171;font-size:.85rem;margin-bottom:4px">' + esc(w.issue) + '</div>' +
      '<div style="font-size:.78rem;color:#94a3b8">' + esc(w.consequence) + '</div>' +
    '</div>'
  ).join('') || '<p style="color:#475569;font-size:.8rem">No data.</p>';

  document.getElementById('algo-updates').innerHTML = (data.algorithm_updates||[]).map(u =>
    '<div style="display:flex;gap:14px;padding:12px;background:#0f172a;border-radius:8px">' +
      '<div style="font-size:.72rem;color:#64748b;width:80px;flex-shrink:0;padding-top:2px">' + esc(u.date) + '</div>' +
      '<div><div style="font-size:.85rem;color:#f8fafc">' + esc(u.update) + '</div>' +
           '<div style="font-size:.75rem;color:#818cf8;margin-top:4px">' + esc(u.impact) + '</div></div>' +
    '</div>'
  ).join('') || '<p style="color:#475569;font-size:.8rem">No updates logged.</p>';
}

// ── GROWTH HACKS ──────────────────────────────────────────────────────────────
function buildHacks() {
  const viral = DATA.viral_loops || {};
  const adv   = DATA.employee_advocacy || {};
  const part  = DATA.partnerships || {};
  const geoP  = DATA.geo_content_plan || {};

  document.getElementById('viral-loops').innerHTML = (viral.viral_loops||[]).map(l =>
    '<div style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:12px">' +
      '<div style="font-weight:600;color:#a5b4fc;margin-bottom:4px">' + esc(l.name) + '</div>' +
      '<div style="font-size:.78rem;color:#94a3b8;margin-bottom:6px">' + esc(l.mechanics) + '</div>' +
      '<div style="font-size:.72rem;color:#4ade80">Viral coeff: ' + esc(l.expected_viral_coefficient) + '</div>' +
    '</div>'
  ).join('') || '<p style="color:#475569;font-size:.8rem">Run python run.py growth-hacks</p>';

  const partItems = [...(part.saas_partners||[]).map(p =>
    '<div style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:10px">' +
      '<div style="font-weight:600;color:#a5b4fc;font-size:.85rem">' + esc(p.company) + '</div>' +
      '<span class="chip chip-purple">' + esc(p.collaboration_type) + '</span>' +
      '<div style="font-size:.75rem;color:#64748b;margin-top:4px">' + esc(p.why) + '</div>' +
    '</div>'
  ), ...(part.influencers||[]).map(p =>
    '<div style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:10px">' +
      '<div style="font-weight:600;color:#a5b4fc;font-size:.85rem">👤 ' + esc(p.name) + '</div>' +
      '<span class="chip chip-amber">' + esc(p.audience_size) + '</span>' +
      '<div style="font-size:.75rem;color:#64748b;margin-top:4px">' + esc(p.relevance) + '</div>' +
    '</div>'
  )];
  document.getElementById('partnerships').innerHTML = partItems.join('') ||
    '<p style="color:#475569;font-size:.8rem">Run python run.py growth-hacks</p>';

  const onboard = adv.onboarding || {};
  const cs = adv.content_system || {};
  document.getElementById('advocacy').innerHTML = [
    '<div class="card"><h3 style="color:#818cf8;font-size:.85rem">Onboarding</h3><ul style="font-size:.78rem;color:#94a3b8;line-height:1.8">' + listHtml(onboard.steps) + '</ul></div>',
    '<div class="card"><h3 style="color:#818cf8;font-size:.85rem">Content System</h3>' +
      '<div style="font-size:.78rem;color:#94a3b8;margin-bottom:8px">' + esc(cs.sharing_cadence) + '</div>' +
      '<ul style="font-size:.75rem;color:#64748b;line-height:1.8">' + listHtml(cs.content_types) + '</ul></div>',
    '<div class="card"><h3 style="color:#818cf8;font-size:.85rem">KPIs</h3><ul style="font-size:.78rem;color:#94a3b8;line-height:1.8">' + listHtml(adv.kpis) + '</ul></div>',
  ].join('');

  const geoItems = geoP.content_pieces||[];
  if (geoItems.length) {
    document.getElementById('geo-plan-card').style.display = '';
    document.getElementById('geo-plan-list').innerHTML = geoItems.slice(0,6).map(p =>
      '<div style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:12px;display:flex;gap:10px">' +
        '<div style="flex-shrink:0;width:24px;height:24px;border-radius:50%;background:#6366f1;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;color:#fff">' + (p.priority||'–') + '</div>' +
        '<div><div style="font-weight:600;color:#f8fafc;font-size:.85rem">' + esc(p.title) + '</div>' +
        '<div style="font-size:.72rem;color:#64748b;margin-top:2px">' + esc(p.format) + ' · ' + esc(p.publish_on) + ' · ' + esc(p.estimated_length) + '</div></div>' +
      '</div>'
    ).join('');
  }
}

// ── WEEKLY REPORTS ────────────────────────────────────────────────────────────
function buildReports() {
  const reports = DATA.weekly_reports || [];
  if (!reports.length) {
    document.getElementById('reports').innerHTML = '<h1>Weekly Reports</h1>' + noData('weekly reports','python run.py weekly 1 3000');
    return;
  }

  // Growth chart
  const ctx = document.getElementById('growth-chart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: reports.map(([fn,r]) => 'Week ' + (r.week||fn)),
      datasets: [{
        label: 'Followers', fill: true, tension: 0.4, pointRadius: 4,
        borderColor: '#6366f1', backgroundColor: '#6366f130',
        data: reports.map(([,r]) => (r.metrics||{}).current_followers||0),
      }]
    },
    options: { plugins: { legend: { display: false } },
      scales: { x: { ticks: { color: '#64748b' }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: '#334155' } } } }
  });

  document.getElementById('reports-list').innerHTML = reports.map(([fn, r]) => {
    const m = r.metrics||{};
    return '<div class="card">' +
      '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">' +
        '<div style="width:36px;height:36px;border-radius:50%;background:#6366f1;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;color:#fff">W' + (r.week||'?') + '</div>' +
        '<div><div style="font-weight:600;color:#f8fafc">Week ' + (r.week||'?') + ' Report</div><div style="font-size:.72rem;color:#64748b">' + esc(fn) + '</div></div>' +
        '<span class="chip ' + (m.on_track ? 'chip-green' : 'chip-red') + '" style="margin-left:auto">' + (m.on_track ? '✓ On Track' : '⚠ Behind') + '</span>' +
      '</div>' +
      '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px">' +
        [['Followers',m.current_followers],['Target',m.target_at_week],['Variance',m.variance],['Growth',m.growth_rate]]
          .map(([l,v]) => '<div style="text-align:center;background:#0f172a;border-radius:8px;padding:8px">' +
            '<div style="font-weight:700;color:#f8fafc">' + esc(v) + '</div>' +
            '<div style="font-size:.7rem;color:#64748b">' + l + '</div></div>').join('') +
      '</div>' +
      '<div style="font-size:.85rem;color:#94a3b8;margin-bottom:10px">' + esc(r.performance_summary) + '</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">' +
        '<div><div style="font-size:.72rem;color:#4ade80;font-weight:600;margin-bottom:4px">✅ What Worked</div><ul style="font-size:.75rem;color:#64748b;line-height:1.7">' + listHtml(r.what_worked) + '</ul></div>' +
        '<div><div style="font-size:.72rem;color:#f87171;font-weight:600;margin-bottom:4px">❌ What Didn\'t Work</div><ul style="font-size:.75rem;color:#64748b;line-height:1.7">' + listHtml(r.what_didnt_work) + '</ul></div>' +
      '</div>' +
    '</div>';
  }).join('');
}

// ── GENERATED CONTENT ─────────────────────────────────────────────────────────
function buildContent() {
  const content = DATA.generated_content || [];
  if (!content.length) {
    document.getElementById('content').innerHTML = '<h1>Generated Content</h1>' + noData('generated content','python run.py content post "your topic"');
    return;
  }
  document.getElementById('content-list').innerHTML = content.map(([fn, c]) =>
    '<div class="card">' +
      '<div style="font-size:.72rem;color:#64748b;margin-bottom:8px">' + esc(fn) + '</div>' +
      '<pre style="font-size:.72rem;color:#94a3b8;background:#0f172a;border-radius:8px;padding:12px;overflow:auto;max-height:200px;white-space:pre-wrap">' + esc(JSON.stringify(c, null, 2)) + '</pre>' +
    '</div>'
  ).join('');
}

// ── INIT ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const builders = [buildOverview, buildCompetitive, buildGeo, buildPlaybook,
                    buildCalendar, buildAlgorithm, buildHacks, buildReports, buildContent];
  builders.forEach(fn => { try { fn(); } catch(e) { console.error(fn.name, e); } });
});
</script>
</body>
</html>"""
