# Desktop Application

**File:** `desktop_app.py`

**Purpose:**
This script serves as the **entry point** for the Desktop version of the Dye Machine Dashboard. It initializes the web server, configures the application environment, and orchestrates the integration of data, layout, and interactivity components.

**Key Responsibilities:**

1.  **Initialization:**
    -   Sets up the `Flask` server and `Dash` application instance.
    -   Configures external stylesheets (Bootstrap) and server security keys.
    -   Initializes the `DatabaseConnection` and verifies connectivity.

2.  **Data Loading:**
    -   Fetches the initial dataset for all charts using `get_all_charts_data`.
    -   This pre-loaded data is passed to the layout to ensure the dashboard renders with content immediately upon load.

3.  **Layout Construction:**
    -   Calls `create_desktop_layout` to build the visual structure of the dashboard.
    -   Injects the fetched `data` and default configuration settings (language="zh_cn", theme="black", period="今天").

4.  **Callback Registration:**
    -   Acts as the central hub for registering all interactive behaviors.
    -   Imports and calls registration functions from the `callbacks/` module.
    -   Connects the UI components (layout) with the logic (callbacks) for features like:
        -   Time period selection
        -   Theme switching
        -   Chart interactivity
        -   Auto-refresh cycles
        -   Startup configuration modals

**Execution:**
-   When run directly (`__main__`), it starts the server on `0.0.0.0:8051`.
-   It is designed to run in a production-like environment (or dev mode with `debug=True` if uncommented).


