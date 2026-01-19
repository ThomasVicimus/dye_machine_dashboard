# Chart 5: Machine Activity Timeline

**Files:**
- Layout: `PlotCharts/PlotChart_chart5.py`
- Factory: `ChartFactory/chart_factory_chart5.py`
- Callback: `callbacks/select_time_period_callback.py`
- **Config**: `env/dashboard_config.yml`

**Description:**
This chart provides a Gantt-chart style timeline of machine activities and states.

**Desktop Functionality:**
- **`create_chart5_layout`**:
  - Calls `create_chart5_figure` to generate the timeline chart.
  - Wraps the figure in a `dcc.Graph` component.
- **`create_chart5_figure`**:
  - Visualizes machine states (Running, Stop, Pause, etc.) over a time period (24h, 48h, 72h).
  - Uses horizontal bars (`go.Bar` with `orientation='h'`) to represent activity duration.
  - Colors bars based on the machine state.
  - Displays batch numbers inside the bars.
  - Adds a vertical dashed line to indicate the current time.
  - Supports dynamic height adjustment based on the number of machines.

---

## Centralized Configuration

Lane counts (number of machines shown per page) are now controlled via **`env/dashboard_config.yml`**:

```yaml
charts:
  lane_count:
    desktop: 8      # lanes shown on desktop dashboard
    mobile: 4       # lanes shown on mobile dashboard

chart5:
  default_timeframe: "24_hrs"   # initial timeframe: 24_hrs | 48_hrs | 72_hrs
```

**How to change settings:**
1. Edit `env/dashboard_config.yml`
2. Restart the app

**Config loader:** `function/dashboard_config.py` provides helper functions:
- `get_lane_count("desktop")` / `get_lane_count("mobile")` → lane count
- `get_chart5_default_timeframe()` → default timeframe string

> **Note:** The config file is cached in memory at startup. No performance overhead from repeated reads.

---

## How lane count flows through the code

Chart 5 uses **paging-by-slicing** – the callback slices the dataframe to a subset of machines per page.

### Where lane count is applied

| Location | Purpose |
|----------|---------|
| `PlotCharts/PlotChart_chart5.py` | **Initial render** – sets `page_size` / `mobile_page_size` from config |
| `callbacks/select_time_period_callback.py` | **Primary control** – slices dataframe on every update using config values |
| `ChartFactory/chart_factory_chart5.py` | Accepts `page_size` parameter to add dummy lanes for consistent height |

### Desktop lane count
- **Initial render**: `PlotCharts/PlotChart_chart5.py` → `create_chart5_layout(..., page_size=get_lane_count("desktop"))`
- **Callback updates**: `callbacks/select_time_period_callback.py` → `register_chart5_timeframe_callbacks(..., page_size_desktop=...)`

### Mobile lane count
- **Initial render**: `PlotCharts/PlotChart_chart5.py` → `create_chart5_layout(..., mobile_page_size=get_lane_count("mobile"))`
- **Callback updates**: `callbacks/select_time_period_callback.py` → `register_chart5_timeframe_callbacks(..., page_size_mobile=...)`

---

## Detail page (mobile)

The mobile detail page for Chart 5 shows **all machines in one chart** (no lane limiting). This is driven by `callbacks/detail_page_callbacks.py` which calls `create_chart5_figure(...)` using the full dataset for the selected timeframe.

---

## Matching Chart 2 and Chart 5 lane counts

Both Chart 2 (DataTable) and Chart 5 (Timeline) now share the same lane count configuration under `charts.lane_count`. This ensures visual consistency across the dashboard.

To change both at once:
1. Edit `env/dashboard_config.yml`:
   ```yaml
   charts:
     lane_count:
       desktop: 10   # Both Chart 2 and Chart 5 will show 10 lanes on desktop
       mobile: 5     # Both will show 5 lanes on mobile
   ```
2. Restart the app
