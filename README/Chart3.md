# Chart 3: Production Output

**Files:**
- Layout: `PlotCharts/PlotChart_chart3.py`
- Factory: `ChartFactory/chartfactory_chart3.py`

**Description:**
This chart displays production output trends and summary statistics.

**Desktop Functionality:**
- **`create_chart3_layout`**:
  - Calls `create_chart3_txtcards_layout` to generate summary text cards.
  - Calls `create_chart3_figure` to generate the main line chart.
  - Combines the text cards and the graph into a single `html.Div`.
- **`create_chart3_txt_cards`**:
  - Calculates and returns three summary cards:
    1.  **Total Output**: Total weight (kg) produced in the period.
    2.  **Max Output**: The machine with the highest output and its value.
    3.  **Min Output**: The machine with the lowest output and its value.
- **`create_chart3_figure`**:
  - Visualizes the trend of "weight_kg" over time (dates).
  - Draws a line chart with markers showing production output.
  - Handles empty or invalid data by displaying an empty chart with an error message.


