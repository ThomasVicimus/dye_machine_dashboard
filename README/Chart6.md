# Chart 6: Stop Reasons

**Files:**
- Layout: `PlotCharts/PlotChart_chart6.py`
- Factory: `ChartFactory/chartfactory_chart6.py`

**Description:**
This chart analyzes machine downtime reasons.

**Desktop Functionality:**
- **`create_chart6_layout`**:
  - Calls `create_chart6_txt_cards` to generate summary cards.
  - Calls `create_chart6_figure` to generate the bar charts.
  - Arranges them in a 2-column layout:
    - Left: Large "Overall Statistics" card.
    - Right: Combined "Highest/Lowest" cards and the bar chart.
- **`create_chart6_txt_cards`**:
  - Generates 3 cards:
    1.  **Overall**: Total idle hours and average idle hours per machine.
    2.  **Highest Idle**: Machine with the most downtime.
    3.  **Lowest Idle**: Machine with the least downtime.
- **`create_chart6_figure`**:
  - Creates side-by-side bar charts showing the stop reasons for:
    1.  **Highest Idle Machine**: Reasons contributing to the downtime of the worst-performing machine.
    2.  **Lowest Idle Machine**: Reasons for the best-performing machine (if any).
  - Maps reason codes (e.g., "reason1") to display names using a configuration file.


