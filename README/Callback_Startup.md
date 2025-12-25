# Startup Modal Callbacks

**File:** `callbacks/startup_modal_callbacks.py`

**Description:**
This module manages the sequence of initialization modals that appear when the application first loads. It guides the user through selecting the initial configuration: Time Period -> Timeframe (for Chart 5) -> Theme.

**Key Functions:**

-   **`register_startup_modal_callbacks`**:
    -   **Sequence Logic**:
        1.  **Period Modal OK**:
            -   Closes `period-modal`.
            -   Updates `time-period-store` with the selected value.
            -   Opens `timeframe-modal`.
        2.  **Timeframe Modal OK**:
            -   Closes `timeframe-modal`.
            -   Updates `chart5-timeframe-store`.
            -   Opens `theme-modal`.
        3.  **Theme Modal OK**:
            -   Closes `theme-modal`.
            -   Updates `theme-store`.
            -   (Dashboard is now fully visible and configured).
    -   **Inputs**: "OK" button clicks on each modal (`n_clicks`).
    -   **State**: Radio button values from each modal.


