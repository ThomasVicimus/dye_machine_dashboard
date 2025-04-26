from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
import os
from datetime import datetime

# Import from new modules
from layouts.mobile_dashboard_layout import create_main_dashboard_layout
from callbacks.mobile_page_callbacks import register_mobile_page_callbacks

# Import necessary components from existing modules
from database_connection import db  # Assuming get_MachineUsage_data needs this
from chart_factory_MachineUasge import (
    MachineUsageChart,
    get_MachineUsage_data,
)  # Actual factory and data func
from callbacks_chart_machine_usage import (
    load_initial_chart1_data,
    create_chart1_layout,
    # create_period_buttons_chart1, # Not directly used here anymore
    # register_chart1_callbacks, # Not directly used here anymore
    PERIOD_STORE_ID as CHART1_PERIOD_STORE_ID,  # Still need the ID
)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_mobile")

# Initialize Dash app for Mobile
mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,  # Needed for multi-page structure
)

# Instantiate ChartFactory
# Assuming lang='zh_cn' is correct, adjust if needed
chart_factory = MachineUsageChart({}, lang="zh_cn")

# * Load initial data and figures
(
    initial_chart1_figure,
    placeholder_chart_figure,  # Use the one from load_initial_chart1_data
    chart1_available_periods,
    chart1_default_period,
) = load_initial_chart1_data(mobile=True)


# Define a wrapper for the data loading function needed by the detail page callback
# This handles database connection if get_MachineUsage_data requires it directly
def load_data_for_detail_view(period):
    conn = None
    try:
        conn = db.connect()
        data = get_MachineUsage_data(
            conn, specific_period=period
        )  # Pass period if function supports it
        # If get_MachineUsage_data returns all periods, filter here:
        # all_data = get_MachineUsage_data(conn)
        # data = {period: all_data.get(period)} if period in all_data else {}
        return data
    except Exception as e:
        logger.error(
            f"Error loading data for detail view (period: {period}): {e}", exc_info=True
        )
        return {}  # Return empty dict on error
    finally:
        if conn:
            db.close(conn)


# --- Mobile Layout Definition ---
# The layout is now simpler, just holding the URL and page content container
mobile_app.layout = html.Div(
    [
        dcc.Location(id="mobile-url", refresh=False),
        dcc.Store(
            id=CHART1_PERIOD_STORE_ID,
            storage_type="session",
            data=chart1_default_period,
        ),
        html.Div(id="mobile-page-content"),
    ]
)

# --- Register Callbacks ---


# Define a function that returns the main layout (needed by the callback)
# This closure captures the necessary variables
def get_main_layout_func():
    return create_main_dashboard_layout(
        create_chart1_layout, initial_chart1_figure, placeholder_chart_figure
    )


# Register the page display callbacks
register_mobile_page_callbacks(
    app=mobile_app,
    chart_factory=chart_factory,
    chart1_default_period=chart1_default_period,
    chart1_period_store_id=CHART1_PERIOD_STORE_ID,
    load_data_func=load_data_for_detail_view,  # Pass the wrapper function
    layout_func=get_main_layout_func,  # Pass the function that returns the layout
)


# Register other callbacks if needed (e.g., interval update)
@mobile_app.callback(
    Output("mobile-dynamic-content", "children"),
    Input("mobile-interval", "n_intervals"),
    prevent_initial_call=True,
)
def update_mobile_content(n):
    # Check if the target element exists in the current layout using clientside callback might be better,
    # but for now, just update if the interval triggers.
    triggered_id = callback_context.triggered_id
    if triggered_id == "mobile-interval":
        # This might still raise errors if the main dashboard isn't visible.
        # Consider making Output dependent on URL or using clientside checks.
        try:
            # Attempt to update, will fail if 'mobile-dynamic-content' not present
            return f"Last update: {datetime.now().strftime('%H:%M:%S')}"
        except Exception as e:
            logger.warning(
                f"Could not update mobile-dynamic-content (likely not visible): {e}"
            )
            return dash.no_update
    return dash.no_update


# --- Server Start ---
if __name__ == "__main__":
    logger.info("Starting mobile server...")
    mobile_app.run(host="0.0.0.0", port=8051, debug=True)
