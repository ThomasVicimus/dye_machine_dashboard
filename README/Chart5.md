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


