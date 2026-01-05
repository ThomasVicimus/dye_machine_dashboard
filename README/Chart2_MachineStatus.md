# Chart 2: Machine Status

**Files:**
- Layout: `PlotCharts/PlotChart_MachineStatus.py`
- Factory: `ChartFactory/chartfactory_chart2.py`

**Description:**
This chart displays the real-time status of machines in a tabular format.

**Desktop Functionality:**
- **`create_chart2_layout`**:
  - Retrieves machine status data from the provided DataFrames.
  - Calls `create_chart2_figure` to generate the table.
  - Wraps the table in an `html.Div` that includes a `dcc.Interval` for auto-pagination (default 15 seconds).
- **`create_chart2_figure`**:
  - Creates a `dash_table.DataTable` to display machine status details.
  - Configures pagination based on `desktop_row_count` (default 8 rows per page).
  - Applies styling for headers and cells (colors, fonts, alignment).
  - Returns the DataTable component.

## Mobile main page: auto page turning logic

Chart 2 uses a `dcc.Interval` + callback to automatically advance the DataTable page.

### How it works
- **Interval lives in the layout**: `PlotCharts/PlotChart_MachineStatus.py:create_chart2_layout(...)`
  - Creates `dcc.Interval(id="chart-2-interval", interval=page_interval * 1000, n_intervals=0)`
- **Page turning callback**: `callbacks/refresher_callback.py:register_chart2_page_turner(app)`
  - Updates `Output("chart-2", "page_current")`
  - Trigger: `Input("chart-2-interval", "n_intervals")`
  - Uses `State("chart-2", "page_count")` to wrap around:
    - keeps current page when `n_intervals == 0` (prevents starting on page 2)
    - otherwise returns `((page_current or 0) + 1) % page_count`

### Where to change the timing
- Edit **`page_interval`** (seconds) in:
  - `PlotCharts/PlotChart_MachineStatus.py:create_chart2_layout(..., page_interval=15, ...)`

### Where to change rows per page (lane count for the table)
- Desktop / mobile rows-per-page are controlled by:
  - `PlotCharts/PlotChart_MachineStatus.py:create_chart2_layout(..., desktop_row_count=8, mobile_row_count=4, ...)`
  - and used by `ChartFactory/chartfactory_chart2.py:create_chart2_figure(...)`

### Important: ensure the callback is registered for mobile
- Auto page turning only works if `register_chart2_page_turner(app)` is called by the app.
  - It is called in `desktop_app.py`
  - If you want the same behavior on **mobile main**, also call it in `mobile_app.py`


