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


def create_chart1_layout(initial_figure, mobile: bool = False, href: str | None = None):
    """Creates the dbc.Col layout containing just the graph for chart 1."""
    if not mobile:
        return dbc.Col(
            [
                dcc.Graph(
                    id=CHART_ID, figure=initial_figure, config={"displayModeBar": False}
                )
            ],
            width=4,
            className="p-2",
        )
    else:
        graph_component = dcc.Graph(
            id=f"mobile-{CHART_ID}",
            figure=initial_figure,
            style={
                "height": "20vh",
                "width": "95%",
            },  # Height adjusted
            config={"displayModeBar": False},
        )

        # If href is provided, wrap the graph in a dcc.Link
        if href:
            content = dcc.Link(
                graph_component,
                href=href,
                id=f"link-mobile-{CHART_ID}",
                # Add style to make the link occupy the full space if needed
                style={"display": "block", "height": "100%", "width": "100%"},
            )
        else:
            content = graph_component

        return dbc.Col(
            [content],  # Place the content (Graph or Link wrapping Graph) here
            width=4,  # Width changed
            className="p-0",
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
