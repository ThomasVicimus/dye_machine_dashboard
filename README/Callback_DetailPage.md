# Detail Page Callbacks

**File:** `callbacks/detail_page_callbacks.py`

**Description:**
This module manages the interactions and routing for the mobile detail views. It handles URL changes based on user clicks (specifically table row clicks) and renders the appropriate detailed chart or table view.

**Key Functions:**

-   **`register_table_click_url_push`**:
    -   **Purpose**: Enables navigation from the Chart 2 summary table to its detail view.
    -   **Triggers**: User clicks a cell (`active_cell`) in the Chart 2 table (`chart-2`).
    -   **Action**: Updates the URL path to `/details/chart-2`, triggering the main routing callback.
    -   **Logic**:
        -   Listens to `active_cell` on the table.
        -   Ignores clicks if they are related to pagination or empty cells.
        -   Pushes the new pathname to the `mobile-url` location component.

-   **`register_detail_page_callbacks`**:
    -   **Purpose**: The central router for the mobile application's detail pages.
    -   **Triggers**: Changes to the URL pathname (`mobile-url`).
    -   **Action**: Renders the specific content for the requested chart ID into the `mobile-page-content` div.
    -   **Logic**:
        -   **Route Parsing**: Checks if the path starts with `/details/`. Extracts the `chart_id`.
        -   **Data Retrieval**: Fetches the correct dataset (period data, timeframe data, or desktop data) from the stores based on the `chart_id`.
        -   **Deserialization**: Deserializes the dataframe from the `all-chart-data-store`.
        -   **Content Generation**:
            -   **Tables**: If the chart is a table (like Chart 2), calls the table factory (`create_chart2_figure_detail`).
            -   **Charts**: If it's a visual chart, calls the specific `create_..._detail` factory function from the `charts_var` mapping.
        -   **Layout Construction**: Wraps the generated figure/table in a responsive, scrollable layout with a "Back" button and a title. It handles both single figures and lists of figures (e.g., one chart per machine).
        -   **Error Handling**: Displays a friendly error page if data is missing or deserialization fails.


