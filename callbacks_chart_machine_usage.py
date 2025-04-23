import dash
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback_context, ALL
import json
import logging

from database_connection import db
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data

logger = logging.getLogger(__name__)

# Constants for component IDs to avoid typos and ensure uniqueness
CHART_ID = "chart-1"
PERIOD_STORE_ID = "selected-period-store-chart1"
BUTTON_TYPE = "period-button-chart1"
BUTTON_CONTAINER_ID = "period-button-container-chart1"

# ---- Data Loading ----


def load_initial_chart1_data():
    """Fetches initial data and creates the first figures for chart 1."""
    initial_figure = go.Figure().update_layout(title="Loading...")
    placeholder_figure = go.Figure().update_layout(title="...")
    available_periods = []
    default_period = None

    try:
        conn = db.connect()
        # Assume get_MachineUsage_data returns dict: {period: {"avg": df, "best": df, "worst": df}}
        dfs_chart1 = get_MachineUsage_data(conn)
        db.close(conn)

        available_periods = list(dfs_chart1.keys())
        if not available_periods:
            logger.warning("No periods found in dfs_chart1 data.")
            default_period = "No Data"
            initial_figure = go.Figure().update_layout(title="No Data Available")
            placeholder_figure = initial_figure
        else:
            default_period = available_periods[0]
            logger.info(f"Chart 1: Available periods: {available_periods}")
            logger.info(f"Chart 1: Default period: {default_period}")

            chart_factory = MachineUsageChart(
                {}, lang="zh_cn"
            )  # Create factory instance here
            initial_figure = chart_factory.create_machine_usage_chart(
                default_period,
                dfs_chart1,
                # TODO: Pass dynamic sizes if needed
            )
            # Use the same figure for other placeholders initially
            placeholder_figure = initial_figure

    except Exception as e:
        logger.error(
            f"Error during initial data fetching or chart creation for Chart 1: {e}",
            exc_info=True,
        )
        if "conn" in locals() and conn:  # Ensure connection is closed on error
            db.close(conn)
        default_period = "Error"
        initial_figure = go.Figure().update_layout(title="Error Loading Chart 1")
        placeholder_figure = go.Figure().update_layout(title="Error Loading Chart")

    return initial_figure, placeholder_figure, available_periods, default_period


# ---- Layout Components ----


def create_period_buttons_chart1(periods):
    """Creates the ButtonGroup for period selection for chart 1."""
    if not periods or periods == ["No Data"] or periods == ["Error"]:
        return dbc.Alert("No periods available", color="warning", className="mb-2")
    return dbc.ButtonGroup(
        [
            dbc.Button(
                period,
                id={"type": BUTTON_TYPE, "index": period},
                color="primary",
                outline=True,
                size="sm",
            )
            for period in periods
        ],
        className="mb-2",
    )


def create_chart1_layout(initial_figure):
    """Creates the dbc.Col layout containing just the graph for chart 1."""
    return dbc.Col(
        [
            dcc.Graph(
                id=CHART_ID, figure=initial_figure, config={"displayModeBar": False}
            )
        ],
        width=4,
        className="p-2",
    )


# ---- Callback Registration ----


def register_chart1_callbacks(app):
    """Registers callbacks for chart 1 interactivity."""

    chart_factory = MachineUsageChart(
        {}, lang="zh_cn"
    )  # Create factory instance for callbacks

    @app.callback(
        Output(PERIOD_STORE_ID, "data"),
        Input({"type": BUTTON_TYPE, "index": ALL}, "n_clicks"),
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
        Input(PERIOD_STORE_ID, "data"),
        # TODO: Add screen size/theme inputs if needed for dynamic chart sizing
        prevent_initial_call=True,
    )
    def update_chart1_figure(selected_period):
        logger.info(f"Chart 1: Updating figure for period: {selected_period}")
        if not selected_period or selected_period in ["No Data", "Error"]:
            return go.Figure().update_layout(title=f"Invalid Period: {selected_period}")

        try:
            conn_update = db.connect()
            dfs_update = get_MachineUsage_data(conn_update)
            db.close(conn_update)

            if selected_period not in dfs_update:
                logger.warning(
                    f"Chart 1: Selected period '{selected_period}' not found in updated data."
                )
                return go.Figure().update_layout(
                    title=f"Data not found for {selected_period}"
                )

            # TODO: Add dynamic sizing based on screen/theme inputs
            new_figure = chart_factory.create_machine_usage_chart(
                selected_period,
                dfs_update,
            )
            return new_figure

        except Exception as e:
            logger.error(
                f"Chart 1: Error updating figure for period {selected_period}: {e}",
                exc_info=True,
            )
            if "conn_update" in locals():  # Ensure connection closed on error
                db.close(conn_update)
            return go.Figure().update_layout(
                title=f"Error loading data for {selected_period}"
            )

    logger.info("Chart 1 callbacks registered.")
