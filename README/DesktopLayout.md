# Desktop Dashboard Layout

**File:** `layouts/desktop_dashboard_layout.py`

**Description:**
This module defines the main structure and layout of the desktop version of the dashboard. It orchestrates the arrangement of the 6 individual charts and handles global state components.

**Key Components:**
-   **`create_desktop_layout`**: The main function that returns the Dash layout tree.
    -   **Inputs**:
        -   `initial_charts_data`: Dictionary containing initial DataFrames for all charts.
        -   `color_theme`: Selected color theme (e.g., "black", "dark_blue").
        -   `lang`: Selected language (e.g., "en", "zh_cn", "zh_hk").
        -   `default_period`: Initial time period for data (e.g., "今天").
    -   **Structure**:
        -   **Data Stores**:
            -   `all-chart-data-store`: Client-side store for chart data.
            -   `theme-store`: Stores current theme.
            -   `time-period-store` & `chart5-timeframe-store`: Session storage for selected timeframes.
        -   **Grid Layout**:
            -   **Row 1**: Displays Chart 1 (Machine Usage), Chart 2 (Machine Status), and Chart 3 (Production) side-by-side.
            -   **Row 2**: Displays Chart 4 (Energy), Chart 5 (Timeline), and Chart 6 (Stop Reasons) side-by-side.
            -   Uses `dash_bootstrap_components` (`dbc.Row`, `dbc.Col`, `dbc.Card`) for responsive alignment.
        -   **Modals**:
            -   **Period Selection**: Popup for selecting the global time period.
            -   **Chart 5 Timeframe**: Specific popup for Chart 5 (24h/48h/72h).
            -   **Theme Selection**: Popup for changing the dashboard color theme.
    -   **Integration**:
        -   Imports and calls individual layout creation functions from `PlotCharts`:
            -   `create_chart1_layout`
            -   `create_chart2_layout`
            -   `create_chart3_layout`
            -   `create_chart4_layout`
            -   `create_chart5_layout`
            -   `create_chart6_layout`

