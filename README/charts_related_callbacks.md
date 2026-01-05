# Chart-Related Callbacks

This document lists the callbacks that directly affect the visualization, data, or state of the charts in the dashboard.

## Overview

| Callback Function | Related Charts | File | Description |
| :--- | :--- | :--- | :--- |
| `register_time_period_callbacks` | Chart 1, 3, 4, 6 | `callbacks/select_time_period_callback.py` | Updates the main figure for these charts when the global time period changes or data auto-refreshes. It deserializes data and calls the respective chart factory. |
| `register_chart5_timeframe_callbacks` | Chart 5 | `callbacks/select_time_period_callback.py` | Manages the specific 24h/48h/72h timeframe for Chart 5. Handles data slicing for pagination and updates the timeline figure. |
| `register_txt_cards_callbacks` | Chart 3, 6 | `callbacks/select_time_period_callback.py` | Updates the summary text cards (e.g., Total Output, Max/Min Machine) associated with these charts when the period or data changes. |
| `register_chart2_data_refresh_callback` | Chart 2 | `callbacks/select_time_period_callback.py` | Updates the data content of the Machine Status table (Chart 2) whenever the global data store is refreshed. |
| `register_theme_callbacks` | Chart 2 | `callbacks/select_theme_callback.py` | Dynamically updates the styling (header color, row colors, status cell colors) of the Chart 2 table to match the selected application theme. |
| `register_chart2_page_turner` | Chart 2 | `callbacks/refresher_callback.py` | Implements auto-pagination for the Chart 2 table, cycling through pages of machine status data on a timer. |
| `register_auto_refresh_callbacks` | All Charts | `callbacks/select_time_period_callback.py` | Triggers a global data fetch every 60 seconds. Updates the `all-chart-data-store`, which cascades to trigger all other data-dependent chart callbacks. |

## Detailed Explanations

### Chart 1 (Machine Usage)
- **`register_time_period_callbacks`**: Listens for changes in `time-period-store` (e.g., "Today", "Yesterday"). It regenerates the pie charts using `MachineUsageChart.create_machine_usage_chart` with the new period's data.

### Chart 2 (Machine Status)
- **`register_chart2_data_refresh_callback`**: Ensures the table shows the latest status (Running, Stopped, etc.) by pushing new data to the `data` property of the DataTable.
- **`register_theme_callbacks`**: Modifies the `style_data_conditional` property to apply theme-consistent colors and status-specific highlighting (Green/Red/Yellow).
- **`register_chart2_page_turner`**: Updates the `page_current` property of the DataTable based on a timer, creating a slideshow effect for long lists of machines.

### Chart 3 (Production Volume)
- **`register_time_period_callbacks`**: Regenerates the line chart (`create_chart3_figure`) showing production trends for the selected period.
- **`register_txt_cards_callbacks`**: Recalculates and updates the three summary cards (Total Output, Max Machine, Min Machine) based on the new period's data.

### Chart 4 (Machine Waste/Energy)
- **`register_time_period_callbacks`**: Regenerates the bar charts (`create_chart4_figure`) for Energy/Water/Steam consumption based on the selected period.

### Chart 5 (Machine Activity Timeline)
- **`register_chart5_timeframe_callbacks`**:
    - **Timeframe**: Updates based on `chart5-timeframe-store` (24h, 48h, 72h).
    - **Pagination**: Because Chart 5 can be tall, this callback slices the dataframe to show a subset of machines (e.g., 8 machines) and rotates through them using the same interval timer as Chart 2.
    - **Figure**: Calls `create_chart5_figure` with the sliced data to render the Gantt chart.

### Chart 6 (Stop Reasons)
- **`register_time_period_callbacks`**: Regenerates the bar charts (`create_chart6_figure`) showing stop reasons for the highest/lowest idle machines.
- **`register_txt_cards_callbacks`**: Updates the summary cards (Overall Idle, Highest Idle Machine, Lowest Idle Machine) for the selected period.

