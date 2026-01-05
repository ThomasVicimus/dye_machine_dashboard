# Mobile Dashboard – 3-Track Plan (Layout / Charts / Host)

This plan intentionally separates work into **three tracks** so we don’t mix concerns (UI contracts vs chart rendering vs deployment). The recommended execution order is: **Layout → Charts → Host**.

---

## 1) Layout Track (mobile UI + routing + “contracts”)

### Goal
Lock down the **mobile UI contracts** that everything else depends on:
- component IDs
- stores (selected period/timeframe, serialized chart data)
- routing (`/details/<chart-id>`)
- card sizing + scroll behavior
- click-to-detail behavior (link or clickData)

### Work items
- **Stabilize stores and IDs**
  - Confirm `dcc.Store` IDs and payload shape:
    - `all-chart-data-store` contains `"<chart-id>-data-store"` keys
    - `time-period-store` contains the selected period key
    - `chart5-timeframe-store` contains the selected timeframe key
  - Ensure all chart components use consistent IDs (`chart-1` … `chart-6`)

- **Standardize navigation to detail**
  - For now, use Option A:
    - **Option A (current)**: `dcc.Link` wraps the chart card
    - **Option B (more polished)**: callback `clickData → mobile-url.pathname`
    Option B will be in TODOs
  - Keep chart-2 table navigation via `active_cell → /details/chart-2`


- **Detail page “container contract”**
  - Ensure `callbacks/detail_page_callbacks.py` always renders into `mobile-page-content`
  - Ensure the detail wrapper is scrollable and not fighting the main dashboard scroll
  - Standardize detail `dcc.Graph` height rules for:
    - **single-figure detail** (full-height)
    - **list-of-figures detail** (row-figures stacked; consistent height per row)

### Done criteria
- Tapping each chart card reliably routes to `/details/chart-x`
- Detail page renders and scrolls correctly for:
  - chart-2 (table component)
  - chart-4/6 (list-of-figures)
  - chart-1 (list-of-figures)
- IDs/stores are stable enough that chart work won’t require re-touching layout/callback IDs later

---

## 2) Charts Track (ChartFactory mobile completeness + consistency)

### Goal
Make the mobile charts **functionally comparable to desktop**, using a consistent pattern:
- **Mobile main**: light “overview” figure that fits the dashboard card
- **Mobile detail**: complete detail view, typically “all machines, 3 per row”

### Standard contract (apply to charts 1–6)
For each chart:
- **Main**: `create_chartX_figure_mobile_main(period, dfs, ...) -> go.Figure`
- **Detail**: `create_chartX_figure_detail(period, dfs, ...) -> go.Figure | List[go.Figure]`

### Per-chart work items
- **Chart 1**
  - Polish `MachineUsageChart.create_machine_usage_chart_mobile_main`
  - Polish `MachineUsageChart.create_machine_usage_chart_mobile_all_machine`:
    - ensure stable 3-per-row “all machines” layout
    - consistent heights/margins/title/legend behavior

- **Chart 2**
  - Main: keep mobile table readable (font sizes, column widths)
  - Detail: ensure `create_chart2_figure_detail` is mobile-friendly (no pagination, scroll OK)

- **Chart 3**
  - Main is OK (overview trend)
  - Refactor detail from “many lines in one figure” into **list-of-figures**:
    - Figure 0: overview
    - Figures 1..N: **3 machines per row figure** (match chart-1/4/6 mental model)

- **Chart 4**
  - Already has mobile main + list-of-figures detail
  - Align style (row heights, margins, legend policy) with Chart 1

- **Chart 5 (special case)**
  - Main should be **readable** by showing **4 lanes per page** (4 machines shown at once):
    - implement a variable like `mobile_page_size = 4` (or a function argument) so it’s easy to change later
    - main chart height stays stable; user reads a small set of lanes clearly
  - Click/tap the chart card to open `/details/chart-5`
  - Detail should show **all machines at once** in **one chart** (single `go.Figure`):
    - do **not** limit lanes in detail
    - allow the figure height to grow based on machine count
    - user scrolls the **detail page** to view the full timeline
  - Ensure timeframe selection integrates cleanly with detail routing (24/48/72h):
    - main: default timeframe (e.g. 24h)
    - detail: respects `chart5-timeframe-store` and/or provides controls on detail page later

- **Chart 6**
  - Already has list-of-figures detail
  - Align style with Chart 1 (row heights, margins, legend placement)

### Done criteria
- On the dashboard, each chart shows a **mobile-optimized main figure**
- Each detail route returns the correct thing:
  - chart-2 returns a table component
  - charts that should show all machines return `List[go.Figure]` with **3-per-row**
- Consistent theme styling (background transparency, font color, margins)

---

## 3) Host Track (how the mobile app is served)

### Goal
Make the mobile app accessible reliably in your target environment (LAN / reverse proxy / cloud), without disturbing layout/chart work.

### Work items
- **Decide deployment shape**
  - Same host/port as desktop with different base path? (e.g. `/mobile`)
  - Separate port? (e.g. desktop `8051`, mobile `8052`)
  - Reverse proxy front (nginx/IIS) rewriting paths?

- **Make host settings configurable**
  - Use environment variables for:
    - host IP (`0.0.0.0` vs specific LAN IP)
    - port
    - base path / url prefix (if needed)
    - `SECRET_KEY` (never hardcode in prod)

- **Validate routing with chosen host setup**
  - Confirm `/` loads dashboard
  - Confirm `/details/chart-x` works directly when opened (deep link)
  - Confirm static assets and websocket/socketio (if used) behave correctly behind proxy

### Done criteria
- Mobile dashboard is reachable from a phone on the target network
- Deep links to `/details/chart-x` work
- Host/port/prefix settings are controlled via env vars (not hardcoded)


