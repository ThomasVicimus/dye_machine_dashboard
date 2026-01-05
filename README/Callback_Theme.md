# Select Theme Callbacks

**File:** `callbacks/select_theme_callback.py`

**Description:**
This module handles the application's visual theming, allowing users to switch between color schemes (e.g., "black" and "dark_blue"). It ensures that the dashboard background, text, and specific components like the data table adapt to the selected theme.

**Key Functions:**

-   **`register_theme_callbacks`**:
    -   **Theme Selection**:
        -   **Input**: User clicks a "theme-button".
        -   **Output**: Updates `theme-store` with the selected theme key.
    -   **Apply Global Theme**:
        -   **Input**: Changes to `theme-store`.
        -   **Output**: Updates the style of the main `dashboard-content` div (background color, text color).
    -   **Update Table Theme (Chart 2)**:
        -   **Input**: Changes to `theme-store` or chart data.
        -   **Output**: Dynamically updates the styling of the Chart 2 `DataTable` (`style_header`, `style_data_conditional`, `style_cell`).
        -   **Logic**:
            -   Retrieves common styles (header color, alternating row colors) based on the theme.
            -   Applies conditional formatting to the status column (Green for "Running", Yellow for "Paused", Red for "Stopped") to ensure status visibility matches the theme context.
    -   **Update Detail Table Theme**:
        -   Similar logic for updating the theme of the mobile detail view tables (`mobile-detail-chart-chart-2-0`).


