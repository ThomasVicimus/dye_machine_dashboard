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


