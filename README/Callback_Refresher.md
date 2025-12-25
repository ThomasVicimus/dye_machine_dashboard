# Refresher Callback

**File:** `callbacks/refresher_callback.py`

**Description:**
This module implements the auto-pagination logic for the Chart 2 (Machine Status) table.

**Key Functions:**

-   **`register_chart2_page_turner`**:
    -   **Purpose**: Automatically cycles through pages of the machine status table to show all machines over time.
    -   **Triggers**: `chart-2-interval` (n_intervals).
    -   **Logic**:
        -   Reads the current page (`page_current`) and total page count (`page_count`).
        -   Increments the page index by 1.
        -   Uses modulo arithmetic (`% page_count`) to loop back to the first page after reaching the last one.
        -   Includes a check to prevent skipping the first page on initial load.


