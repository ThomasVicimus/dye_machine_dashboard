# Mobile Dashboard Plan (Charts 1–6)

## 1) Current architecture (what exists today)

- **Entry point**: `mobile_app.py`
  - Loads all chart datasets once via `get_all_charts_data(db)`
  - Passes data into `layouts/mobile_dashboard_layout.py:create_mobile_layout(...)`
  - Registers callbacks, including **mobile detail routing** in `callbacks/detail_page_callbacks.py`

- **Main mobile layout**: `layouts/mobile_dashboard_layout.py`
  - Renders a 2×3 grid of “chart cards”
  - Stores:
    - `dcc.Store(id="all-chart-data-store")`: serialized data for *all charts*
    - `dcc.Store(id="time-period-store")`: selected period key (e.g. `"今天"`)
    - `dcc.Store(id="chart5-timeframe-store")`: chart-5 timeframe key (e.g. `"24_hrs"`)
  - Navigation:
    - Charts **1, 3, 4, 5, 6**: main chart area is wrapped by `dcc.Link(href="/details/<chart-id>")`
    - Chart **2**: table click is handled by callback `register_table_click_url_push` (active cell → URL)

- **Detail page routing**: `callbacks/detail_page_callbacks.py`
  - Parses URL `/details/<chart-id>`
  - Picks the corresponding factory from `charts_var`
  - Pulls serialized chart data from `all-chart-data-store` via key `"<chart-id>-data-store"`
  - Deserializes data via `Database.serialize_df:deserialize_dataframe_dict`
  - Calls the chart factory:
    - **Tables** (chart-2): returns a Dash component (DataTable)
    - **Charts**: returns either **one `go.Figure`** or **a `List[go.Figure]`**
  - UI supports scroll, and already renders **lists of figures** (currently stacked vertically)

## 2) Target mobile UX (consistent across Chart 1–6)

- **Mobile main card (dashboard page)**:
  - Lightweight, fast-to-render figure (“overview”)
  - No modebar, responsive sizing, minimal text, readable in ~40vh card

- **Tap-to-detail**:
  - User taps the chart card → navigates to `/details/chart-x`

- **Detail page**:
  - Scrollable, full width
  - For “per machine” detail: show **all machines, 3 columns per row** (same idea as Chart 1’s `_mobile_all_machine`)
  - For charts where 3-col “tiles” don’t fit well (e.g. timeline): provide a paged/stacked “rows” approach with consistent height per section

## 3) Standardize the “mobile chart contract” (refactor guideline)

### 3.1 One consistent interface per chart

For each chart X, standardize to:

- **Main**: `create_chartX_figure_mobile_main(period, dfs, *, lang="zh_cn", theme="black", ...) -> go.Figure`
- **Detail**: `create_chartX_figure_detail(period, dfs, *, lang="zh_cn", ...) -> Union[go.Figure, List[go.Figure]]`

Notes:
- Chart 1 already uses:
  - `MachineUsageChart.create_machine_usage_chart_mobile_main(...)`
  - `MachineUsageChart.create_machine_usage_chart_mobile_all_machine(...) -> List[Figure]`
- Chart 4 already has:
  - `create_chart4_figure_mobile(...)` (main)
  - `create_chart4_figure_detail(...) -> List[Figure]` (detail; 3-per-row)
- Chart 6 already has:
  - `create_chart6_figure(...)` (main)
  - `create_chart6_figure_detail(...) -> List[Figure]` (detail; 3-per-row)

### 3.2 Shared mobile styling helpers (recommended)

Create a small helper module (example path: `ChartFactory/mobile_style.py`) with:

- `apply_mobile_main_layout(fig, *, title=None, margin=..., font=..., legend=...)`
- `apply_mobile_detail_layout(fig, *, height_px=..., margin=..., legend=...)`
- Shared constants:
  - background transparency: `paper_bgcolor="rgba(0,0,0,0)"`, `plot_bgcolor="rgba(0,0,0,0)"`
  - font color: `#fdfefe`
  - row figure height guidance: 220–300px per “row figure”

This keeps Chart 1–6 visually consistent and reduces copy/paste layout tweaking.

### 3.3 Optional: replace `dcc.Link` with `clickData` navigation (UX polish)

`dcc.Link` wrapping a `dcc.Graph` is simple, but it can interfere with “tap/hold” interactions and makes it hard to distinguish “tap to open” vs “scroll/zoom”.

Alternative (recommended for polish):
- Keep `dcc.Graph(id="chart-x")` as-is on the dashboard
- Add a callback per chart:
  - `Input("chart-x", "clickData")` → `Output("mobile-url", "pathname")` to push `/details/chart-x`
- Keep Chart 2’s table click callback as-is

This produces a more “native” feel and avoids anchor-link edge cases.

## 4) Per-chart plan (what to build/refactor)

### Chart 1 (设备使用率) — baseline to copy

- **Main** (`MachineUsageChart.create_machine_usage_chart_mobile_main`) should remain “single overview”:
  - Keep **Avg** only (fast + readable)
  - Polish: title placement, legend spacing, consistent margins inside a 40vh card

- **Detail** (`MachineUsageChart.create_machine_usage_chart_mobile_all_machine`) is the reference:
  - Ensure it always returns:
    - Figure 0: summary row (Avg/Best/Worst)
    - Figures 1..N: all machines, **3 machines per figure**
  - Polish:
    - consistent `row_height_px` for each figure
    - make subplot titles readable (truncate long machine names)
    - only show legend on the summary (or first) figure

### Chart 2 (总覽表) — table UX

- **Main**:
  - Keep the paginated table (`create_chart2_layout(..., mobile=True)`)
  - Consider (later): reduce columns or add conditional formatting for status for readability on small screens

- **Detail**:
  - `create_chart2_figure_detail(df)` already exists and works with the router
  - Polish:
    - ensure horizontal scroll + sticky header if needed
    - adjust `minWidth` and font-size for common phone widths

### Chart 3 (生产量) — make “detail” match the multi-row pattern

Current:
- Main uses `create_chart3_figure(...)` (order_index==0 “overall trend”), which is fine.
- Detail uses `create_chart3_figure_detail(...)` which returns **one figure with many machine lines** (can get cluttered).

Plan:
- Keep **main** as-is (overview).
- Refactor **detail** to return `List[Figure]` with a consistent “row” layout:
  - Figure 0: “overall trend” (order_index==0) + optional annotations
  - Figures 1..N: **3 machines per figure** (1×3 subplots), each subplot is a simple per-machine sparkline/line
    - Use same pagination pattern as chart-4 detail (chunk machines in groups of 3)
    - Keep axes minimal; show machine name as subplot title; optionally show last value as annotation

Why:
- This matches the Chart 1 / Chart 4 / Chart 6 “3 per row” mental model for users.

### Chart 4 (资源消耗) — already mostly complete

Current:
- `create_chart4_figure_mobile(...)` is a good mobile main (Avg only).
- `create_chart4_figure_detail(...) -> List[Figure]` already implements:
  - summary row
  - all machines in 3-per-row figures

Plan:
- Align styling (margins / heights / titles) to Chart 1:
  - unify row heights with Chart 1/6
  - ensure consistent legend rules (legend only on summary)

### Chart 5 (设备活动时间线) — special case (timeline)

Current:
- Main uses `create_chart5_figure(...)` with mobile-optimized margins.
- Detail is also `create_chart5_figure(...)` and returns a single tall figure (can be very tall).

Plan (two options; pick one):

- **Option A (fast)**: keep single-figure detail, but improve usability
  - Move/enable timeframe buttons on the **detail page** (24/48/72h) to reduce clutter on dashboard
  - Ensure y-axis label sizing and left margin are tuned for phones

- **Option B (best UX)**: implement paged detail as `List[Figure]`
  - Add `create_chart5_figure_detail(period, dfs, page_size=8, page_index=0/...) -> List[Figure]`
  - Return multiple “pages” as stacked figures, each showing `page_size` machines
  - This keeps scrolling predictable and makes the chart less “infinite height”

Even though Chart 5 doesn’t map to “3 columns per row”, it should still follow the **“detail can return list-of-figures”** contract like other charts.

### Chart 6 (设备停机原因) — already mostly complete

Current:
- Main uses text cards + 2-subplot figure (highest vs lowest).
- Detail already returns `List[Figure]`:
  - Figure 0: summary (highest vs lowest)
  - Figures 1..N: **3 machines per figure**, with top reasons per machine

Plan:
- Align style and sizing with Chart 1 / Chart 4:
  - unify row heights
  - ensure legend policy (avoid duplicate legends; consistent placement)

## 5) Callback/router plan (small refactors for consistency)

### 5.1 Centralize chart definitions

`callbacks/detail_page_callbacks.py:charts_var` is already the right idea.
Refactor it slightly to be more uniform:

- Each entry should clearly declare:
  - `chart_factory_detail` (detail builder)
  - `chart_title`
  - `data_key_resolver` (how to choose `period`/`timeframe`/`desktop`)

This removes chart-specific `if chart_id == ...` in the routing callback.

### 5.2 Ensure the detail page layout supports “row figures”

The current detail renderer stacks figures vertically at full width, which is fine because each “row” is already a 1×3 subplot figure for charts 1/4/6 (and will be for chart 3 after refactor).

Polish ideas:
- Use a consistent `dcc.Graph` height for row figures (e.g. 280–320px) instead of `"45vh"`
- Add small separators between rows (padding/margin)

## 6) Implementation order (recommended)

- **Milestone 1 (pattern complete)**:
  - Chart 1: polish main + detail sizing
  - Chart 4: align styling with chart 1
  - Chart 6: align styling with chart 1

- **Milestone 2 (hardest chart)**:
  - Chart 3: refactor detail into list-of-figures, 3-per-row

- **Milestone 3 (special)**:
  - Chart 5: choose Option A or B and implement

- **Milestone 4 (table UX)**:
  - Chart 2: refine mobile + detail table styling, confirm click routing edge cases

## 7) Definition of “done” for mobile charts

- **Main**:
  - Renders fast, readable inside 40vh card
  - Tap opens detail view reliably

- **Detail**:
  - Scrollable, stable performance
  - For machine-based charts: all machines visible, **3 machines per row**
  - Consistent margins, font sizes, background transparency, and legend behavior


