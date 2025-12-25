# Select Time Period Callbacks

**File:** `callbacks/select_time_period_callback.py`

**Description:**
This module manages the core data flow and interactivity related to time period selection and data updates for the charts. It registers callbacks that respond to user inputs (button clicks) and system events (auto-refresh intervals).

**Key Functions:**

-   **`register_time_period_callbacks`**:
    -   **Triggers:** User clicks a "period-button" (e.g., "Today", "Yesterday").
    -   **Action:** Updates the `time-period-store` with the selected period string.
    -   **Chart Updates**: Registers individual callbacks for Charts 1, 3, 4, and 6. When `time-period-store` or `all-chart-data-store` changes:
        1.  Retrieves serialized data for the specific chart.
        2.  Deserializes it into pandas DataFrames.
        3.  Calls the appropriate chart factory function (desktop or mobile) to generate a new Plotly figure.
        4.  Updates the chart component (`Output(CHART_ID, "figure")`).

-   **`register_chart5_timeframe_callbacks`**:
    -   **Triggers:** User clicks a "chart5-timeframe-button" (e.g., "24h", "48h").
    -   **Action:** Updates `chart5-timeframe-store`.
    -   **Chart 5 Update**: Listens to timeframe changes and auto-refresh intervals. It handles:
        -   Retrieving and deserializing Chart 5 data.
        -   **Pagination**: Slices the dataframe to show a subset of machines (default 8 per page) based on the current interval count.
        -   Generating the timeline figure using `create_chart5_figure`.

-   **`register_txt_cards_callbacks`**:
    -   **Triggers:** Changes to `time-period-store` or `all-chart-data-store`.
    -   **Action:** Updates the summary text cards for Chart 3 and Chart 6.
    -   Calls the respective factory functions (`create_chart3_txt_cards`, `create_chart6_txt_cards`) to generate updated card components.

-   **`register_auto_refresh_callbacks`**:
    -   **Triggers:** `mobile-interval` (default 60 seconds).
    -   **Action:** Fetches fresh data from the database using `get_all_charts_data`.
    -   **Storage**: Serializes the new data and updates `all-chart-data-store`. This update cascades to all other callbacks listening to the store, ensuring the entire dashboard reflects the latest database state.

-   **`register_chart2_data_refresh_callback`**:
    -   **Triggers:** Changes to `all-chart-data-store`.
    -   **Action:** Updates the data and columns of the Chart 2 `DataTable` with the latest machine status information.


