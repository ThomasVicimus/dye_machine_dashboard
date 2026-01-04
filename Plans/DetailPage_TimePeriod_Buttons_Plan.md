# Detail Page Time-Period Buttons Plan (Mobile)

## Goal
When a user opens a chart detail page (`/details/chart-x`), show a **time-period button group** at the **top-right** of the popup detail header. Clicking a period button updates the detail chart(s) to that period. The **default** selection should be the **currently selected period** (stored in `time-period-store`).

## Current state (relevant pieces)
- **Layout**
  - `layouts/mobile_dashboard_layout.py` provides:
    - `dcc.Location(id="mobile-url")`
    - `dcc.Store(id="time-period-store")` (current selected period)
    - `dcc.Store(id="all-chart-data-store")` (serialized datasets per chart)
    - `html.Div(id="mobile-page-content")` (detail overlay container)
- **Detail routing + rendering**
  - `callbacks/detail_page_callbacks.py:register_detail_page_callbacks`
    - callback currently triggers only on `Input("mobile-url", "pathname")`
    - reads period/timeframe as `State(...)`
    - renders charts using `data_key = period_data` for most charts
- **Buttons**
  - `layouts/create_buttons.py:create_period_button(periods)`
    - returns a ButtonGroup with IDs:
      - `{"type": "period-button", "index": period}`
    - (currently does not show “selected/active” state)
- **Period selection callbacks**
  - `callbacks/select_time_period_callback.py:register_time_period_callbacks(...)`
    - already exists and is registered in `mobile_app.py`
    - (assumed) writes the selected period into `time-period-store`

## Key design decision
We keep **Option A navigation** (chart cards wrapped with `dcc.Link`) and implement period switching on detail pages by:

1) Rendering the period buttons into the **detail header**.
2) Ensuring the **detail page rerenders** when `time-period-store` changes (because currently it’s only a `State`, so nothing updates on click).

## UX spec
- **Placement**
  - Header row contains:
    - Left: Back button
    - Center: Chart title
    - Right: Time period buttons (compact)
- **Behavior**
  - Default period on detail open = `time-period-store.data`
  - Clicking a period:
    - updates `time-period-store.data`
    - updates the detail chart(s) immediately
- **Visibility rules**
  - Show **period buttons** for: chart-1, chart-3, chart-4, chart-6
  - For chart-5, show **timeframe buttons** (24/48/72) instead (already defined as `create_chart5_timeframe_buttons`)
  - For chart-2 (table), hide period buttons (or optionally show but no-op) — recommend **hide**

## Data / callback flow (recommended)

### A) Make detail rendering reactive to store changes (required)
Update the detail-page callback signature in `callbacks/detail_page_callbacks.py`:

- **Before**
  - `Input("mobile-url", "pathname")`
  - `State("time-period-store", "data")`
  - `State("chart5-timeframe-store", "data")`
  - `State("all-chart-data-store", "data")`

- **After**
  - `Input("mobile-url", "pathname")`
  - `Input("time-period-store", "data")`  ← so charts rerender when period changes
  - `Input("chart5-timeframe-store", "data")`  ← so chart-5 rerenders on timeframe change
  - `State("all-chart-data-store", "data")`

Rationale: simplest way to refresh the detail view without adding additional figure-update callbacks.

### B) Render buttons in the detail header (required)
Inside the “detail overlay” layout returned in `display_page(...)`, add a right-side column:

- For charts using period:
  - Call `create_period_button(periods=periods)`
- For chart-5:
  - Call `create_chart5_timeframe_buttons()`
- For chart-2:
  - Render nothing (empty div)

**Where do `periods` come from?**
- Preferred: derive from `deserialized_chart_data` for the current chart, e.g. `periods = list(deserialized_chart_data.keys())` (excluding `"desktop"`).
- Acceptable fallback: derive from `all-chart-data-store["chart-1-data-store"]` periods (global periods), but chart-specific is safer.

### C) Show the currently selected period as “active” (recommended polish)
Update `layouts/create_buttons.py:create_period_button(...)` to accept:

- `selected_period: str | None`

and set button appearance accordingly, e.g.:
- selected: `color="primary"`, `outline=False`
- not selected: `outline=True`

Do the same for chart-5 timeframe buttons:
- `create_chart5_timeframe_buttons(selected_timeframe: str | None)`

This makes it obvious which period is currently applied.

## Implementation steps (in order)

1) **Buttons API update (small + safe)**
   - Update `create_period_button(periods, selected_period=None)`
   - Update `create_chart5_timeframe_buttons(selected_timeframe=None)`

2) **Detail page header update**
   - Modify `callbacks/detail_page_callbacks.py` to render the right-side button group conditionally per chart.
   - Use `selected_period=period_data` (or timeframe store for chart-5) to highlight the current selection.

3) **Make detail page reactive**
   - Change callback Inputs/States as described so the detail page rerenders on store changes.

4) **Verify store update behavior**
   - Ensure existing callbacks in `select_time_period_callback.py` still update `time-period-store` when period buttons are clicked from the **detail page** (pattern-matching IDs remain the same).
   - Ensure chart-5 timeframe callback updates `chart5-timeframe-store`.

5) **Edge cases / fallback behavior**
   - If `period_data` is not present in the chart’s available periods, fall back to the first available period.
   - If data is missing, keep current error handling page.

## Done criteria
- On any detail page for chart-1/3/4/6, period buttons appear at top-right and clicking them updates the chart(s).
- On chart-5 detail page, timeframe buttons appear at top-right and clicking them updates the timeline.
- Chart-2 detail page shows no period buttons.
- The selected period/timeframe is visually indicated.


