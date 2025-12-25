# Chart 1: Machine Usage

**Files:**
- Layout: `PlotCharts/PlotChart_MachineUsage.py`
- Factory: `ChartFactory/chart_factory_MachineUasge.py`

**Description:**
This chart visualizes machine usage statistics.

**Desktop Functionality:**
- **`create_chart1_layout`**:
  - Initializes the `MachineUsageChart` factory.
  - Calls `create_machine_usage_chart` to generate the figure.
  - Wraps the figure in a `dcc.Graph` component.
- **`MachineUsageChart.create_machine_usage_chart`**:
  - Takes a dictionary of DataFrames (`dfs`) and a specific period.
  - Extracts "Average", "Best", and "Worst" usage data.
  - Creates a subplot with 3 Pie charts:
    1.  **Average Usage**: Shows the overall average machine usage percentages (Running, Idle, Down, Repair).
    2.  **Best Machine**: Shows the usage percentages for the machine with the best performance.
    3.  **Worst Machine**: Shows the usage percentages for the machine with the worst performance.
  - Returns a Plotly Figure object.


