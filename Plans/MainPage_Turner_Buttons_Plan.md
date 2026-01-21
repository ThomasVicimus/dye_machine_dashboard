# Main Page "Page Turner" Buttons Plan (Chart 2 + Chart 5, Mobile)

## Questions to answer
1) **Can Chart 2's existing paging controls also control Chart 5** on the mobile main page?
2) If not (or if we want better UX), **can we add one set of buttons** that controls **both Chart 2 and Chart 5** at the same time?

---

## Current state (after config refactor – Jan 2026)

### Chart 2 (table)
- Component: `dash_table.DataTable(id="chart-2", page_action="native")`
- **Mobile**: native pagination controls ARE visible (Prev / Next buttons built into DataTable)
- **Desktop**: pagination controls are hidden via CSS (`.previous-next-container { display: none }`)
- Auto page turning callback `register_chart2_page_turner()` is **NOT called** in `mobile_app.py`
  - ✅ This is correct: users click the DataTable's built-in controls
- Lane counts (rows per page) are now pulled from `env/dashboard_config.yml` via `get_lane_count("mobile")` / `get_lane_count("desktop")`

### Chart 5 (timeline)
- Callback: `callbacks/select_time_period_callback.py:register_chart5_timeframe_callbacks(...)`
- **Current paging driver**: `Input("chart-2-interval", "n_intervals")`
  - ⚠️ This is **auto page turning** via the interval timer – NOT click-driven
  - The interval fires every `page_interval` seconds (default 15s from config)
- Lane counts are now pulled from config via `get_lane_count("mobile")` / `get_lane_count("desktop")`

### Problem
Chart 2 is click-only (correct), but Chart 5 is still auto-turning (incorrect for mobile UX).
They are **not synchronized**: clicking Chart 2's pagination does not affect Chart 5.

---

## Key idea
To have "one set of buttons" control both charts, both Chart 2 and Chart 5 need to share a **single source of truth** for "current page index".

There are two good ways to achieve this:

---

## Option A (recommended): reuse Chart 2's existing DataTable paging buttons to drive Chart 5

### What it means
Keep Chart 2 exactly as-is (user clicks the DataTable's built-in page controls), and wire Chart 5 to **listen to Chart 2's current page**.

### How it works
- Modify Chart 5 update callback:
  - **Remove**: `Input("chart-2-interval", "n_intervals")` as page driver
  - **Add**: `Input("chart-2", "page_current")` as the page driver
  - Optionally add `State("chart-2", "page_count")` for wrap-around logic
- In Chart 5 slicing logic, replace:
  ```python
  current_interval = n_intervals or 0
  current_page_idx = current_interval % page_count
  ```
  With:
  ```python
  current_page_idx = (page_current or 0) % page_count
  ```

### Why this answers your question
Yes: **the same "buttons" (Chart 2's built-in paging UI) can control Chart 5**, because Chart 5 will page according to whatever Chart 2 is currently showing.

### Files to edit
- `callbacks/select_time_period_callback.py`
  - In `register_chart5_timeframe_callbacks(...)`:
    - Change `Input("chart-2-interval", "n_intervals")` → `Input("chart-2", "page_current")`
    - (Optional) Add `State("chart-2", "page_count")` if you want to clamp
    - Line ~87-90: remove/change the interval input
    - Line ~170-172: change `current_interval = n_intervals or 0` → `current_page_idx = (page_current or 0) % page_count`

### Pros / cons
- **Pros**: minimal UI work; no new buttons; preserves "click-only" preference; both charts stay synchronized
- **Cons**: Chart 5 paging becomes "coupled" to Chart 2 being present on the page (it is, in your current layout)

---

## Option B: add a shared page-turner ButtonGroup controlling both Chart 2 and Chart 5

### What it means
Add explicit "Prev / Next" buttons (and optionally a page indicator) on the dashboard. Clicking these buttons advances a shared page index, which:
- sets `chart-2.page_current`
- slices machines for chart-5

### UI spec
- Location: top row of the mobile dashboard (near where the period/theme buttons previously were), or as a sticky footer toolbar
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
- **Pros**: explicit UX; decouples Chart 5 from Chart 2; works even if Chart 2 layout changes later
- **Cons**: more code/UI work; must decide what "page count" means (use Chart 2's page_count, or compute from Chart 5 machine count)

---

## Recommendation
Start with **Option A** (reuse Chart 2 paging UI to drive Chart 5) because it matches your current UX ("click-only paging, buttons already shown on dashboard") and is the smallest change.

If later you want a cleaner unified control bar, implement **Option B**.

---

## "Done" criteria (Option A)
- On mobile main page:
  - User clicks Chart 2 next/prev
  - Chart 2 switches page
  - **Chart 5 switches to the corresponding page** and shows **exactly N lanes** (from config, default 4 for mobile)
- No auto page turning occurs on mobile.
- Both charts use the same lane count from `env/dashboard_config.yml`.

---

## Implementation checklist (Option A)

- [ ] Edit `callbacks/select_time_period_callback.py`:
  - [ ] Change `Input("chart-2-interval", "n_intervals")` to `Input("chart-2", "page_current")`
  - [ ] Update paging logic from interval-based to `page_current`-based
- [ ] Test on mobile:
  - [ ] Click Chart 2 pagination
  - [ ] Verify Chart 5 updates to matching page
  - [ ] Verify no auto page turning
