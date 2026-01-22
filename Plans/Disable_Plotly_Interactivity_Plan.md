# Disable Plotly Interactivity (Mobile-first) – Plan

## Goal
On the **dashboard** (and optionally detail pages), prevent Plotly graphs from “stealing” touch gestures:
- user scrolls the page → page scrolls (not graph zoom/pan)
- user taps a chart card → navigates to detail (not graph drag/hover)

We do **not** need Plotly interactivity, so we should disable it consistently across the app.

---

## What’s currently happening
- `dcc.Graph` components are created in multiple places (PlotCharts modules + `callbacks/detail_page_callbacks.py`).
- Most graphs already set `config={"displayModeBar": False, "responsive": True}` but **do not** set Plotly’s non-interactive flags.
- On mobile/touch devices, Plotly will capture gestures for:
  - drag to pan/select
  - pinch zoom / scroll zoom (depending)
  - double-tap interactions
This can conflict with “scroll page” and “tap to open detail”.

---

## Recommended technical approach

### A) Standardize a single “non-interactive config”
Use Plotly/Dash Graph config flags:

- `staticPlot: True`  ✅ strongest “no interaction” mode
- `scrollZoom: False`
- `displayModeBar: False`
- `doubleClick: False`
- `responsive: True`
- `displaylogo: False`

Example config dict:

```python
NON_INTERACTIVE_GRAPH_CONFIG = {
    "staticPlot": True,
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": False,
    "responsive": True,
    "displaylogo": False,
}
```

This should stop Plotly from intercepting touch/scroll in most cases.

### B) Add a CSS fallback if any device still “steals scroll”
If some mobile browsers still behave poorly, add a targeted CSS rule on the **dashboard tiles only**:

- `.mobile-dashboard-page .js-plotly-plot { pointer-events: none; }`

Important:
- This must be scoped carefully because it will also disable hover/click inside plots.
- It should **not** be applied to pages where you might want hover/tooltips later.

---

## Where to apply it (repo-wide)

### 1) Dashboard charts (highest priority)
Update all PlotCharts that render the dashboard `dcc.Graph`:
- `PlotCharts/PlotChart_MachineUsage.py` (chart-1)
- `PlotCharts/PlotChart_chart3.py` (chart-3)
- `PlotCharts/PlotChart_chart4.py` (chart-4)
- `PlotCharts/PlotChart_chart5.py` (chart-5)
- `PlotCharts/PlotChart_chart6.py` (chart-6)

Set every dashboard `dcc.Graph(..., config=NON_INTERACTIVE_GRAPH_CONFIG)`.

Chart-2 is a DataTable, not Plotly; no change needed.

### 2) Detail pages (optional, but recommended for consistency)
`callbacks/detail_page_callbacks.py` dynamically creates `dcc.Graph` for detail figures.
- Update those `dcc.Graph(..., config=...)` blocks to use the same non-interactive config.

If you want *some* interactivity in detail pages later, we can choose:
- dashboard: staticPlot True
- detail: staticPlot False but keep scrollZoom False (less aggressive)

---

## Refactor for maintainability (recommended)

### Create a single config helper
Add a small module, e.g.:
- `function/dash_graph_config.py` (or `layouts/graph_config.py`)

Export:
- `NON_INTERACTIVE_GRAPH_CONFIG`
- (optional) `DETAIL_GRAPH_CONFIG`

Then import and reuse everywhere.

This avoids copying config dicts across many files.

---

## Validation checklist
- On mobile dashboard:
  - swipe scroll always scrolls the dashboard
  - tap on any chart card reliably opens detail
  - no “plot drag rectangle” appears
- On detail pages:
  - swipe scroll always scrolls the detail overlay
  - graphs render normally (static)

---

## Estimated effort
- Config-only approach: **~0.5–1 hour**
- If CSS fallback needed + tuning scope: **~1–2 hours**


