# Main Page “Page Turner” Buttons Plan (Chart 2 + Chart 5, Mobile)

## Questions to answer
1) **Can Chart 2’s existing paging controls also control Chart 5** on the mobile main page?
2) If not (or if we want better UX), **can we add one set of buttons** that controls **both Chart 2 and Chart 5** at the same time?

## Current behavior (mobile main)
- **Chart 2 (table)**
  - Component: `dash_table.DataTable(id="chart-2", page_action="native")`
  - Paging: user clicks the DataTable’s built-in pagination controls (page_next / page_prev).
  - Auto page turning is **not enabled** on mobile because `callbacks/refresher_callback.py:register_chart2_page_turner(app)` is **not called** in `mobile_app.py` (and that matches your desired UX).

- **Chart 5 (timeline)**
  - The current callback in `callbacks/select_time_period_callback.py:register_chart5_timeframe_callbacks(...)` updates `chart-5.figure`.
  - It **can** “page” by slicing the dataframe (machines subset) using `PAGE_SIZE`, but the current driver is `Input("chart-2-interval", "n_intervals")` (reusing Chart 2’s interval) — this is effectively an *auto-page-turn* mechanism.
  - If you want **click-only paging** (no auto), Chart 5 needs a **click-driven page index input**.

## Key idea
To have “one set of buttons” control both charts, both Chart 2 and Chart 5 need to share a **single source of truth** for “current page index”.

There are two good ways to achieve this:

---

## Option A (recommended first): reuse Chart 2’s existing DataTable paging buttons to drive Chart 5

### What it means
Keep Chart 2 exactly as-is (user clicks the DataTable’s built-in page controls), and wire Chart 5 to **listen to Chart 2’s current page**.

### How it works
- Add an input to Chart 5 update callback:
  - `Input("chart-2", "page_current")`
  - (optional) `State("chart-2", "page_count")` for wrap-around logic
- In Chart 5 slicing logic, replace the interval-driven `current_page_idx` with:
  - `current_page_idx = page_current or 0`

### Why this answers your question
Yes: **the same “buttons” (Chart 2’s built-in paging UI) can control Chart 5**, because Chart 5 will page according to whatever Chart 2 is currently showing.

### Files to edit
- `callbacks/select_time_period_callback.py`
  - In `register_chart5_timeframe_callbacks(...)`:
    - remove/reduce reliance on `Input("chart-2-interval", "n_intervals")`
    - add `Input("chart-2", "page_current")` as the page driver
    - use `page_size_mobile=4` lanes for mobile main (already added)

### Pros / cons
- **Pros**: minimal UI work; no new buttons; preserves your “click-only” preference.
- **Cons**: Chart 5 paging becomes “coupled” to Chart 2 being present on the page (it is, in your current layout).

---

## Option B: add a shared page-turner ButtonGroup controlling both Chart 2 and Chart 5

### What it means
Add explicit “Prev / Next” buttons (and optionally a page indicator) on the dashboard. Clicking these buttons advances a shared page index, which:
- sets `chart-2.page_current`
- slices machines for chart-5

### UI spec
- Location: top row of the mobile dashboard (near where the period/theme buttons previously were).
- Buttons:
  - Prev
  - Next
  - Optional: page indicator text (e.g. `1 / N`)

### Data model
- Add a store:
  - `dcc.Store(id="main-page-index-store", data=0, storage_type="session")`
- Optional store:
  - `dcc.Store(id="main-page-count-store", data=1)` (or compute on the fly)

### Callback flow
1) **Button clicks → update `main-page-index-store`**
   - Inputs: Prev/Next `n_clicks`
   - State: `main-page-index-store.data`, `chart-2.page_count` (or computed page count)
   - Output: `main-page-index-store.data`

2) **Drive Chart 2**
   - Output: `chart-2.page_current`
   - Input: `main-page-index-store.data`
   - Optionally clamp modulo `page_count`

3) **Drive Chart 5**
   - In `register_chart5_timeframe_callbacks`, use:
     - `Input("main-page-index-store", "data")` as page index
     - `page_size_mobile=4`
   - Slice machines accordingly.

### Files to edit
- `layouts/create_buttons.py`
  - Add something like `create_main_page_turner_buttons(selected_page=None, page_count=None)`
- `layouts/mobile_dashboard_layout.py`
  - Render the button group and add `main-page-index-store`
- `callbacks/` (new file or extend existing)
  - Add a callback to update `main-page-index-store` on Prev/Next clicks
- `callbacks/select_time_period_callback.py`
  - Change chart-5 paging input to use `main-page-index-store`

### Pros / cons
- **Pros**: explicit UX; decouples Chart 5 from Chart 2; works even if Chart 2 layout changes later.
- **Cons**: more code/UI work; must decide what “page count” means (use Chart 2’s page_count, or compute from Chart 5 machine count).

---

## Recommendation
Start with **Option A** (reuse Chart 2 paging UI to drive Chart 5) because it matches your current UX (“click-only paging, buttons already shown on dashboard”) and is the smallest change.

If later you want a cleaner unified control bar, implement **Option B**.

## “Done” criteria (Option A)
- On mobile main page:
  - User clicks Chart 2 next/prev
  - Chart 2 switches page
  - **Chart 5 switches to the corresponding page** and shows **exactly 4 lanes** (mobile)
- No auto page turning occurs.


