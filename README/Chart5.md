# Chart 5: Machine Activity Timeline

**Files:**
- Layout: `PlotCharts/PlotChart_chart5.py`
- Factory: `ChartFactory/chart_factory_chart5.py`

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

## Changing the number of lanes (machines shown per page)

Chart 5 uses **paging-by-slicing** (it slices the dataframe to a subset of machines per page). This means lane count is controlled primarily by the **callback**, not only by the figure factory.

### Desktop lane count
- **Primary control (what actually limits lanes)**: `callbacks/select_time_period_callback.py`
  - Function: `register_chart5_timeframe_callbacks(...)`
  - Parameter: `page_size_desktop` (default **8**)
- **Secondary/default passed into initial render**: `PlotCharts/PlotChart_chart5.py`
  - Function: `create_chart5_layout(...)`
  - Parameter: `page_size` (default **8**)

### Mobile lane count
- **Primary control (what actually limits lanes)**: `callbacks/select_time_period_callback.py`
  - Function: `register_chart5_timeframe_callbacks(...)`
  - Parameter: `page_size_mobile` (default **4**)
- **Secondary/default passed into initial render**: `PlotCharts/PlotChart_chart5.py`
  - Function: `create_chart5_layout(...)`
  - Parameter: `mobile_page_size` (default **4**)

### Detail page (mobile)
- The mobile detail page for chart-5 is designed to show **all machines in one chart** (no lane limiting). This is driven by `callbacks/detail_page_callbacks.py` which calls `create_chart5_figure(...)` using the full dataset for the selected timeframe.


