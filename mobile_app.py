from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
import os
from datetime import datetime

# Import layout and callback registration
from layouts.mobile_dashboard_layout import create_main_dashboard_layout
from callbacks.mobile_page_callbacks import (
    register_mobile_page_callbacks,
    create_generic_placeholder_figure,  # Import placeholder utility
)

# Import necessary components for chart generation and data
from database_connection import db
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data
from callbacks_chart_machine_usage import (
    load_initial_chart1_data,
    # create_chart1_layout, # Layout creation is now inside mobile_dashboard_layout
    PERIOD_STORE_ID as CHART1_PERIOD_STORE_ID,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_mobile")

# Initialize Dash app
mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Instantiate ChartFactory (needed for chart 1 detail view)
# Ensure this instance is accessible by the detail generator function
# chart_factory = MachineUsageChart({}, lang="zh_cn")

# # * Load initial data and figures for the main dashboard
# (
#     initial_chart1_figure,
#     placeholder_chart_figure,
#     chart1_available_periods,
#     chart1_default_period,
# ) = load_initial_chart1_data(mobile=True)


# --- Detail Figure Generator Functions ---
# Define functions that will generate the detail figure for EACH chart.
# These functions accept the 'period' and handle their own data fetching.


def generate_chart1_detail_fig(period):
    """Generates the detailed figure for Chart 1 (Machine Usage)."""
    conn = None
    try:
        logger.info(f"Generating detail figure for Chart 1, period: {period}")
        conn = db.connect()
        # Use the existing get_MachineUsage_data function
        dfs = get_MachineUsage_data(conn, specific_period=period)
        # Use the specific method from the factory for the detailed mobile view
        figure = chart_factory.create_machine_usage_chart_mobile_all_machine(
            period=period,
            dfs=dfs,
            # Add any other specific parameters needed for the detailed chart
            # plot_height=..., plot_width=...
        )
        return figure
    except Exception as e:
        logger.error(
            f"Error generating detail figure for Chart 1 (period: {period}): {e}",
            exc_info=True,
        )
        return create_generic_placeholder_figure("Error loading Chart 1 details")
    finally:
        if conn:
            db.close(conn)


# --- Placeholder Detail Generators for Charts 2-6 ---
# Replace these with your actual functions


def generate_chart2_detail_fig(period):
    logger.info(f"Generating placeholder detail figure for Chart 2, period: {period}")
    # Replace with actual data fetching and chart creation for Chart 2
    # Example: fetch_data_chart2(period); create_chart2_detail(...) -> fig
    return create_generic_placeholder_figure("Chart 2 Detail (Placeholder)")


def generate_chart3_detail_fig(period):
    logger.info(f"Generating placeholder detail figure for Chart 3, period: {period}")
    return create_generic_placeholder_figure("Chart 3 Detail (Placeholder)")


def generate_chart4_detail_fig(period):
    logger.info(f"Generating placeholder detail figure for Chart 4, period: {period}")
    return create_generic_placeholder_figure("Chart 4 Detail (Placeholder)")


def generate_chart5_detail_fig(period):
    logger.info(f"Generating placeholder detail figure for Chart 5, period: {period}")
    return create_generic_placeholder_figure("Chart 5 Detail (Placeholder)")


def generate_chart6_detail_fig(period):
    logger.info(f"Generating placeholder detail figure for Chart 6, period: {period}")
    return create_generic_placeholder_figure("Chart 6 Detail (Placeholder)")


# --- Map Chart IDs to Generators and Titles ---
detail_figure_generators = {
    "mobile-chart-1": generate_chart1_detail_fig,
    "mobile-chart-2": generate_chart2_detail_fig,
    "mobile-chart-3": generate_chart3_detail_fig,
    "mobile-chart-4": generate_chart4_detail_fig,
    "mobile-chart-5": generate_chart5_detail_fig,
    "mobile-chart-6": generate_chart6_detail_fig,
}

chart_titles = {
    "mobile-chart-1": "Detailed Machine Usage",
    "mobile-chart-2": "Chart 2 Details",
    "mobile-chart-3": "Chart 3 Details",
    "mobile-chart-4": "Chart 4 Details",
    "mobile-chart-5": "Chart 5 Details",
    "mobile-chart-6": "Chart 6 Details",
}

# --- Mobile App Layout ---
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


# Wrapper function to get the main layout (captures figures)
def get_main_layout_func():
    # Pass only the figures needed for the main dashboard view
    return create_main_dashboard_layout(initial_chart1_figure, placeholder_chart_figure)


# Register the page display callbacks with the new structure
register_mobile_page_callbacks(
    app=mobile_app,
    chart1_default_period=chart1_default_period,
    chart1_period_store_id=CHART1_PERIOD_STORE_ID,
    detail_figure_generators=detail_figure_generators,  # Pass the dict of functions
    chart_titles=chart_titles,  # Pass the dict of titles
    layout_func=get_main_layout_func,  # Pass the function that returns the layout
)


# Interval callback remains the same (or can be moved if desired)
@mobile_app.callback(
    Output("mobile-dynamic-content", "children"),
    Input("mobile-interval", "n_intervals"),
    prevent_initial_call=True,
)
def update_mobile_content(n):
    triggered_id = callback_context.triggered_id
    if triggered_id == "mobile-interval":
        try:
            return f"Last update: {datetime.now().strftime('%H:%M:%S')}"
        except Exception as e:
            # Element might not be in the DOM if on detail page
            logger.warning(
                f"Could not update mobile-dynamic-content (likely not visible): {e}"
            )
            return dash.no_update
    return dash.no_update


# --- Server Start ---
if __name__ == "__main__":
    logger.info("Starting mobile server...")
    mobile_app.run(host="0.0.0.0", port=8051, debug=True)
