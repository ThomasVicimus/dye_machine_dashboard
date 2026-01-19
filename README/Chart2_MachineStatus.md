# Chart 2: Machine Status

**Files:**
- Layout: `PlotCharts/PlotChart_MachineStatus.py`
- Factory: `ChartFactory/chartfactory_chart2.py`
- **Config**: `env/dashboard_config.yml`

**Description:**
This chart displays the real-time status of machines in a tabular format.

**Desktop Functionality:**
- **`create_chart2_layout`**:
  - Retrieves machine status data from the provided DataFrames.
  - Calls `create_chart2_figure` to generate the table.
  - Wraps the table in an `html.Div` that includes a `dcc.Interval` for auto-pagination.
- **`create_chart2_figure`**:
  - Creates a `dash_table.DataTable` to display machine status details.
  - Configures pagination based on row count from config.
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

---

## Centralized Configuration

Row counts and page interval are now controlled via **`env/dashboard_config.yml`**:

```yaml
charts:
  lane_count:
    desktop: 8      # rows shown on desktop
    mobile: 4       # rows shown on mobile

chart2:
  page_interval_seconds: 15   # seconds between auto page turns
```

**How to change settings:**
1. Edit `env/dashboard_config.yml`
2. Restart the app

**Config loader:** `function/dashboard_config.py` provides helper functions:
- `get_lane_count("desktop")` / `get_lane_count("mobile")` → row count
- `get_chart2_page_interval()` → page interval in seconds

> **Note:** The config file is cached in memory at startup. No performance overhead from repeated reads.

---

### Where settings are used (after refactor)

| Setting | Config Key | Used By |
|---------|------------|---------|
| Desktop row count | `charts.lane_count.desktop` | `PlotChart_MachineStatus.py`, `chartfactory_chart2.py` |
| Mobile row count | `charts.lane_count.mobile` | `PlotChart_MachineStatus.py`, `chartfactory_chart2.py` |
| Page interval | `chart2.page_interval_seconds` | `PlotChart_MachineStatus.py` |

---

### Important: ensure the callback is registered for mobile
- Auto page turning only works if `register_chart2_page_turner(app)` is called by the app.
  - It is called in `desktop_app.py`
  - If you want the same behavior on **mobile main**, also call it in `mobile_app.py`
