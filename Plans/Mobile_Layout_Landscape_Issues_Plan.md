# Mobile Layout (Landscape) – Issues Investigation & Fix Plan

## Summary of the reported problems
1) **Row 1 should fill the screen; row 2 should require scroll**. Currently both rows are visible so charts are squeezed.
2) **Chart 2 (DataTable) overflows/out of boundary** in the grid.
3) **Charts with text cards (Chart 3, Chart 6)** squeeze the actual chart area.

This plan documents what’s happening today, likely root causes, and the best fix strategy (inline-only vs CSS).

---

## What the current code is doing (facts)

### A) Mobile page container + scrolling
- `layouts/mobile_dashboard_layout.py`
  - Root is fixed: `width=100vw`, `height=100vh`, `overflow="hidden"`
  - Scrolling is on: `#mobile-dashboard-page` with `overflowY="auto"`
  - Two chart rows exist simultaneously in the DOM (Row 1 + Row 2).

### B) Row/Chart heights causing “everything fits”
- Each chart card is explicitly set to **`height: 40vh`** in `mobile_dashboard_layout.py`.
  - Row 1 ≈ 40vh
  - Row 2 ≈ 40vh
  - Total ≈ 80vh (+ margins) → fits inside 100vh → user sees both rows at once → each chart is small/squeezed.

### C) Chart 2 out-of-boundary risk (DataTable behavior)
- Chart 2 layout (`PlotCharts/PlotChart_MachineStatus.py`) wraps:
  - `dcc.Interval`
  - `dash_table.DataTable(id="chart-2", page_action="native")`
- `ChartFactory/chartfactory_chart2.py` mobile table style:
  - `style_table={"width":"100%","height":"100%","overflowX":"auto"}`
  - but DataTable includes pagination controls + header + body which can exceed its parent height unless parent uses a strict flex/overflow pattern.
- Result: DataTable can expand beyond the card boundary and “push” layout.

### D) Text-card layouts squeeze charts by design
- Chart 3 mobile layout (`PlotCharts/PlotChart_chart3.py`) always includes:
  - a **3-card row** + a graph constrained to `height: "80%"`
  - inside a card already constrained by `height: 40vh`
  - the cards consume real vertical space, leaving the chart short.
- Chart 6 mobile layout (`PlotCharts/PlotChart_chart6.py`) uses a **2-column structure**:
  - large card + combined cards + graph, all within a small card → chart area shrinks.

---

## Root causes (why this happens)

### Issue 1: “Both rows visible / charts squeezed”
**Root cause**: fixed heights are too small (`40vh`). The layout is currently designed to show **both rows** within one viewport.

### Issue 2: Chart 2 table out of boundary
**Root cause**: DataTable is not naturally “height-constrained” inside a card without explicit flex/overflow constraints. It can exceed card height due to:
- header + pagination + rows
- intrinsic table sizing rules

### Issue 3: Text cards squeeze charts
**Root cause**: Chart 3 and 6 mobile “main” layouts are reusing desktop-style “cards + chart” compositions inside small dashboard tiles.

---

## Is this complicated with “pure inline HTML styles”?

### What is easy inline
- Changing `40vh` → `100vh` (or similar) to force scrolling.
- Adding wrappers with `overflow:hidden/auto` around specific components.

### What becomes messy inline
Supporting many devices reliably in landscape:
- iOS Safari has “dynamic viewport” behavior; `100vh` can be unstable (address bar changes height).
- You often need `svh/dvh` units and media queries:
  - `100svh` (stable viewport height) is much better for mobile.
- DataTable containment often needs CSS selectors for internal elements.

**Conclusion**: You *can* do a partial fix inline, but a small CSS layer will be much more reliable and less fragile across devices.

---

## Recommended solution approach (practical + robust)

### Phase 1 (quick win): fix row sizing so row-1 fills screen
Goal: show only charts 1–3 in first “screen”, user scrolls to row-2.

- In `layouts/mobile_dashboard_layout.py`:
  - Make **Row 1 container height = 100svh** (or close, e.g. `minHeight: 100svh`)
  - Make **Row 2 container height = 100svh**
  - Inside each row, make chart cards height `100%` so they fill the row.

Implementation detail:
- Introduce CSS classes like `.mobile-row` and `.mobile-chart-card` to avoid repeating inline styles.

### Phase 2: contain Chart 2 DataTable inside its card
Goal: Chart 2 stays within its tile.

Best-practice structure:
- Card body becomes a flex column:
  - header/pagination area fixed
  - table body scrolls inside

Options:
- **Option A (minimal)**: wrap the DataTable in a container `div` with:
  - `height: 100%`, `overflow: hidden`
  - and DataTable `style_table={"height":"100%","overflowY":"auto"}`
- **Option B (better)**: use DataTable props:
  - `fixed_rows={"headers": True}`
  - `style_table={"height":"100%","overflowY":"auto"}`
  - reduce row height / padding on mobile

Files likely involved:
- `PlotCharts/PlotChart_MachineStatus.py`
- `ChartFactory/chartfactory_chart2.py`

### Phase 3: simplify mobile main layout for “text-card charts”
Goal: dashboard tiles prioritize the chart; text summaries move to detail page.

Recommended:
- Chart 3 mobile main tile: **graph only** (no cards)
- Chart 6 mobile main tile: **graph only** (or a compact single summary card + graph, but not the full desktop layout)

Where to implement:
- In the PlotCharts layout modules:
  - `PlotCharts/PlotChart_chart3.py` add a compact mobile path (skip `txtcards_layout`)
  - `PlotCharts/PlotChart_chart6.py` add a compact mobile path (skip large card structure)

This is consistent with how Chart 1/4/5 are designed: “mobile main = overview”.

---

## CSS vs inline: effort estimate

### Inline-only (fast, but fragile)
- **Time**: ~1–3 hours for a “good enough” improvement
- **Risks**:
  - still inconsistent across iOS/Android landscape sizing
  - DataTable quirks may remain on some devices

### Add small CSS layer in `assets/` (recommended)
- Add `assets/mobile.css` with:
  - `@media (orientation: landscape)` rules
  - `.mobile-row { height: 100svh; }`
  - `.mobile-chart-card { height: 100%; overflow: hidden; }`
  - `.chart2-table-wrap { height: 100%; overflow: hidden; }`
- **Time**: ~0.5–1 day to do it cleanly + test on a couple screen sizes
- **Benefits**:
  - far more stable sizing across devices
  - easier to tweak later (one place)

---

## Proposed next steps (what I recommend doing next)
1) Add CSS classes + adjust row heights so Row 1 is a full-screen “page”.
2) Fix Chart 2 DataTable containment inside its tile (wrap + overflow + optional fixed header).
3) Simplify Chart 3 and Chart 6 **mobile main** layouts to “chart-first” (move cards to detail).

If you confirm you’re OK with adding `assets/mobile.css`, we can implement the above in a controlled way with minimal disruption to existing callbacks and IDs.


