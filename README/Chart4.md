# Chart 4: Energy Consumption

**Files:**
- Layout: `PlotCharts/PlotChart_chart4.py`
- Factory: `ChartFactory/chartfactory_chart4.py`

**Description:**
This chart visualizes resource consumption (Water, Power, Steam) per kg of production.

**Desktop Functionality:**
- **`create_chart4_layout`**:
  - Calls `create_chart4_figure` to generate the main chart.
  - Wraps the figure in a `dcc.Graph` component.
- **`create_chart4_figure`**:
  - Creates a subplot with 3 Bar charts comparing resource consumption:
    1.  **Average**: Average consumption across all machines.
    2.  **Best**: Consumption of the most efficient machine.
    3.  **Worst**: Consumption of the least efficient machine.
  - Displays bars for Steam (Yellow), Power (Blue), and Water (Green).
  - Unifies the y-axis scale across subplots for easy comparison.


