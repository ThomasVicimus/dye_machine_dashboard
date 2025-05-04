import dash
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback_context, ALL
import json
import logging
import pandas as pd  # Add pandas import
from Database.serialize_df import deserialize_dataframe_dict

# import pandas as pd # Add if DataFrame reconstruction is needed later

from database_connection import db
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data

logger = logging.getLogger(__name__)

# Constants for component IDs to avoid typos and ensure uniqueness
CHART_ID = "chart-1"
PERIOD_STORE_ID = "selected-period-store-chart1"
CHART1_DATA_STORE_ID = "chart1-data-store"  # Store for pre-fetched data
PERIOD_BUTTON_TYPE = "period-button"
# BUTTON_CONTAINER_ID = "period-button-container-chart1"


# def create_chart1_layout(initial_figure, mobile: bool = False, href: str | None = None):
#     """Creates the dbc.Col layout containing just the graph for chart 1."""
#     if not mobile:
#         return dbc.Col(
#             [
#                 dcc.Graph(
#                     id=CHART_ID, figure=initial_figure, config={"displayModeBar": False}
#                 )
#             ],
#             width=4,
#             className="p-2",
#         )
#     else:
#         graph_component = dcc.Graph(
#             id=f"mobile-{CHART_ID}",
#             figure=initial_figure,
#             style={
#                 "height": "20vh",
#                 "width": "95%",
#             },  # Height adjusted
#             config={"displayModeBar": False},
#         )

#         # If href is provided, wrap the graph in a dcc.Link
#         if href:
#             content = dcc.Link(
#                 graph_component,
#                 href=href,
#                 id=f"link-mobile-{CHART_ID}",
#                 # Add style to make the link occupy the full space if needed
#                 style={"display": "block", "height": "100%", "width": "100%"},
#             )
#         else:
#             content = graph_component

#         return dbc.Col(
#             [content],  # Place the content (Graph or Link wrapping Graph) here
#             width=4,  # Width changed
#             className="p-0",
#         )


# ---- Callback Registration ----


def register_chart1_callbacks(app):
    """Registers callbacks for chart 1 interactivity."""

    chart_factory = MachineUsageChart(
        {}, lang="zh_cn"
    )  # Create factory instance for callbacks

    @app.callback(
        Output(PERIOD_STORE_ID, "data"),
        Input({"type": PERIOD_BUTTON_TYPE, "index": ALL}, "n_clicks"),
        State(PERIOD_STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_selected_period(n_clicks_list, current_period):
        ctx = callback_context
        if not ctx.triggered:
            return current_period

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not button_id:
            return current_period

        try:
            button_info = json.loads(button_id)
            selected_period = button_info.get("index")
            if selected_period:
                logger.info(f"Chart 1: Period button clicked: {selected_period}")
                return selected_period
        except json.JSONDecodeError:
            logger.error(f"Chart 1: Failed to parse button ID: {button_id}")
            return current_period

        return current_period

    @app.callback(
        Output(CHART_ID, "figure"),
        # Trigger directly by period selection AND read data from the store
        Input(PERIOD_STORE_ID, "data"),
        Input(CHART1_DATA_STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_chart1_figure(selected_period, chart1_data):
        # Deserialize the data from the store first
        deserialized_chart1_data = deserialize_dataframe_dict(chart1_data)

        # chart1_data now holds the full dataset loaded at startup
        # selected_period is the newly chosen period
        logger.info(
            f"Chart 1: Updating figure for period: {selected_period} using initially loaded data."
        )

        # Handle cases where initial data loading might have failed or deserialization failed
        if deserialized_chart1_data is None or (
            isinstance(deserialized_chart1_data, dict)
            and "error" in deserialized_chart1_data
        ):
            error_msg = (
                deserialized_chart1_data.get(
                    "error", "Initial data load or deserialization failed"
                )
                if isinstance(deserialized_chart1_data, dict)
                else "Initial data load or deserialization failed"
            )
            logger.warning(
                f"Chart 1: Cannot update figure, data unavailable. Msg: {error_msg}"
            )
            return go.Figure().update_layout(title=f"Error: {error_msg}")

        # Handle cases where the selected period itself is invalid
        if not selected_period or selected_period in ["No Data", "Error"]:
            logger.warning(f"Chart 1: Invalid period selected: {selected_period}")
            return go.Figure().update_layout(
                title=f"Invalid Period Selected: {selected_period}"
            )

        # Data is pre-fetched and now deserialized in deserialized_chart1_data
        dfs_update = deserialized_chart1_data  # Use the deserialized data

        # Check if the selected period exists within the deserialized data
        if selected_period not in dfs_update:
            logger.warning(
                f"Chart 1: Selected period '{selected_period}' not found in initially loaded data."
            )
            # Attempt to find available periods from the loaded data for a better error message
            available_periods = (
                list(dfs_update.keys()) if isinstance(dfs_update, dict) else []
            )
            return go.Figure().update_layout(
                title=f"Data not found for {selected_period}. Available: {available_periods}"
            )

        try:
            # Create the chart using the deserialized data and the selected period
            new_figure = chart_factory.create_machine_usage_chart(
                selected_period,
                dfs_update,  # Pass the deserialized dataset
            )
            return new_figure

        except Exception as e:
            logger.error(
                f"Chart 1: Error generating figure for period {selected_period} from initial data: {e}",
                exc_info=True,
            )
            return go.Figure().update_layout(
                title=f"Error generating chart for {selected_period}"
            )

    logger.info("Chart 1 callbacks registered (using initially loaded data).")
