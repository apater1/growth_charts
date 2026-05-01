# UK-WHO Growth Charts

Two related tools for plotting children's growth on the UK-WHO 0–4 year centile charts:

1. **`girls_growth_charts.py`** — a Python script that renders a static, print-ready PNG chart sheet for girls (Weight-for-age, Length/Height-for-age, Head circumference-for-age) using `matplotlib`.
2. **`web/`** — a small static web app that lets you create child profiles, record measurements over time, and see them plotted live against the same centile lines. All data stays in your browser (`localStorage`); JSON export/import is supported for backups.

🌐 **Live web app:** <https://apater1.github.io/growth_charts/>

## Features (web app)

- Create / edit / delete child profiles (name, sex, date of birth).
- Add weight (kg), length/height (cm) and head circumference (cm) measurements with arbitrary dates.
- Three interactive Plotly charts overlay each measurement on the WHO centiles (0.4 / 2 / 9 / 25 / 50 / 75 / 91 / 98 / 99.6).
- Hover any data point for the exact z-score and computed centile.
- Export the full dataset to JSON; import to merge or replace.
- All data is local to your browser — nothing leaves your device.

## Project layout

```
.
├── girls_growth_charts.py        # matplotlib chart-sheet generator (Python)
├── Boys_0-4_years_growth_chart.pdf   # reference PDFs
├── Girls_0-4_years_growth_chart.pdf
├── web/                          # the static web app
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── lms_data.js           # WHO girls LMS tables (mirrors the Python file)
│       ├── centiles.js           # LMS → value / z-score / centile math
│       ├── store.js              # localStorage CRUD + import/export
│       ├── charts.js             # Plotly rendering
│       └── app.js                # UI controller
└── .github/workflows/            # CI + Pages deployment
```

## Run the web app locally

The page uses native ES modules, so it must be served over HTTP (not `file://`):

```bash
cd web
python3 -m http.server 8765
# open http://127.0.0.1:8765/
```

Any other static server works equally well (`npx http-server`, `php -S`, VS Code Live Server, etc.).

## Run the Python chart generator

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib scipy
python3 girls_growth_charts.py
# produces girls_growth_charts.png
```

## Data sources

- **WHO Child Growth Standards (2006)** — LMS tables for weight, length/height and head circumference, 0–60 months.
- **UK1990 reference** (Cole et al., *Stat Med*, 1998) — used by the UK-WHO charts for the preterm / birth section.

## Disclaimer

This project is provided for **educational use only** and is not a medical device. It must not be used for clinical decision-making. Always consult a qualified healthcare professional for assessment of a child's growth.

## License

MIT — see [`LICENSE`](LICENSE).
