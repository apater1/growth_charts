// Plotly chart rendering for centile charts with measurement overlays.
import {
  CENTILES,
  CENTILE_LABELS,
  buildCurves,
  lmsAt,
  lmsZscore,
  zToCentile,
  REFERENCE_TABLES,
  MEASUREMENTS,
} from './centiles.js';
import { ageInMonths } from './store.js';

const PINK = '#cc0066';
const PINK_DARK = '#aa0055';

// Plotly dash spec per centile (mirrors line_style() in the Python file).
function dashFor(c) {
  if (c === 50) return 'solid';
  if (c === 0.4 || c === 99.6) return 'dash';
  if (c === 2 || c === 98) return 'dot';
  return 'solid';
}
function widthFor(c) {
  if (c === 50) return 2.2;
  if (c === 0.4 || c === 99.6) return 1.2;
  return 1;
}

function centileTraces(table) {
  const { ages, curves } = buildCurves(table);
  return CENTILES.map((c, idx) => ({
    x: ages,
    y: curves[c],
    mode: 'lines',
    name: CENTILE_LABELS[idx],
    line: { color: PINK, width: widthFor(c), dash: dashFor(c) },
    hovertemplate: `${CENTILE_LABELS[idx]} centile<br>Age %{x:.1f}m<br>%{y:.2f}<extra></extra>`,
    showlegend: c === 50 || c === 0.4 || c === 99.6,
  }));
}

function measurementTrace(profile, table, measurementKey, unit) {
  const xs = [];
  const ys = [];
  const text = [];
  profile.measurements.forEach((m) => {
    const value = m[measurementKey];
    if (value == null || value === '') return;
    const ageM = ageInMonths(profile.dob, m.date);
    if (ageM == null) return;
    const { L, M, S } = lmsAt(table, ageM);
    const z = lmsZscore(L, M, S, Number(value));
    const centile = zToCentile(z);
    xs.push(ageM);
    ys.push(Number(value));
    text.push(
      `${m.date}<br>${Number(value).toFixed(2)} ${unit}` +
      `<br>z = ${z.toFixed(2)}<br>centile ≈ ${centile.toFixed(1)}`,
    );
  });
  return {
    x: xs,
    y: ys,
    mode: 'lines+markers',
    name: profile.name,
    line: { color: '#1f4e8c', width: 1.5 },
    marker: { color: '#1f4e8c', size: 8, symbol: 'circle' },
    text,
    hovertemplate: '%{text}<extra></extra>',
  };
}

function layoutFor(title, yLabel, ageMax) {
  return {
    title: { text: title, font: { color: PINK_DARK, size: 14 } },
    margin: { l: 55, r: 30, t: 40, b: 50 },
    paper_bgcolor: 'white',
    plot_bgcolor: '#fafafa',
    xaxis: {
      title: 'Age (months)',
      range: [-0.5, ageMax + 0.5],
      dtick: 3,
      gridcolor: '#dddddd',
      zeroline: false,
    },
    yaxis: {
      title: yLabel,
      gridcolor: '#dddddd',
      zeroline: false,
    },
    legend: {
      orientation: 'h',
      x: 0,
      y: -0.18,
      font: { size: 11 },
    },
    hovermode: 'closest',
  };
}

const CHART_META = {
  weight: { domId: 'chart-weight', title: 'Weight-for-age',          yLabel: 'Weight (kg)' },
  length: { domId: 'chart-length', title: 'Length / Height-for-age', yLabel: 'Length / Height (cm)' },
  head:   { domId: 'chart-head',   title: 'Head circumference-for-age', yLabel: 'Head circ. (cm)' },
};

export function renderCharts(profile) {
  const sexTables = REFERENCE_TABLES[profile.sex];
  if (!sexTables) return;

  // Cap chart x-axis at the latest measurement age (rounded up) or full table range.
  const maxAge = Math.max(
    ...Object.values(sexTables).map((t) => t[t.length - 1][0]),
  );

  MEASUREMENTS.forEach(({ key, label, unit, table }) => {
    const meta = CHART_META[key];
    const lmsTable = sexTables[table];
    const traces = [
      ...centileTraces(lmsTable),
      measurementTrace(profile, lmsTable, key, unit),
    ];
    const layout = layoutFor(meta.title, `${label} (${unit})`, maxAge);
    Plotly.react(meta.domId, traces, layout, {
      displaylogo: false,
      responsive: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    });
  });
}

export function clearCharts() {
  MEASUREMENTS.forEach(({ key }) => {
    const el = document.getElementById(CHART_META[key].domId);
    if (el) Plotly.purge(el);
  });
}
