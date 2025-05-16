import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State
import plotly.graph_objects as go  # Import go for placeholder
from ChartFactory.chart_factory_MachineUasge import MachineUsageChart
from ChartFactory.chartfactory_chart2 import create_chart2_figure_detail
from dash.dependencies import ALL
from dash import callback_context
from Database.serialize_df import deserialize_dataframe_dict

logger = logging.getLogger(__name__)

global PERIOD_STORE_ID
global table_id
global charts_var
global lang

PERIOD_STORE_ID = (
    "time-period-store"  # Ensure this matches the ID in mobile_dashboard_layout.py
)
lang = "zh_cn"
table_id = ["chart-2"]
charts_var = {
    "chart-1": {
        "CHART_ID": "chart-1",
        "chart_factory": MachineUsageChart(
            {}, lang=lang
        ).create_machine_usage_chart_mobile_all_machine,  # Create factory instance for callbacks
        "chart_title": "设备使用率",
    },
    "chart-2": {
        "CHART_ID": "chart-2",
        "chart_factory": create_chart2_figure_detail,
        "chart_title": "总覽表",
    },
}


# Placeholder figure function (can be defined elsewhere too)
def create_generic_placeholder_figure(title="Loading..."):
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": title,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": "#888"},
            }
        ],
        paper_bgcolor="#1a1a1a",
        plot_bgcolor="#1a1a1a",
        margin=dict(l=10, r=10, t=30, b=10),  # Added top margin for title
    )
    return fig


def register_table_click_url_push(app, url_id="mobile-url"):
    @app.callback(
        Output(url_id, "pathname", allow_duplicate=True),
        [Input(f"{cid}", "active_cell") for cid in table_id],
        prevent_initial_call=True,
    )
    def _table_to_url(*active_cells):
        logger.info(f"DETAIL DEBUG: Table click detected")
        triggered = callback_context.triggered_id
        cell = active_cells[
            list(callback_context.inputs).index(f"{triggered}.active_cell")
        ]

        # ignore pagination clicks (active_cell will be {} or missing column_id)
        if not cell or "column_id" not in cell:
            return dash.no_update

        return f"/details/{triggered}"


def register_detail_page_callbacks(
    app,
    default_period,
    lang: str = "zh_cn",
):
    """Registers callbacks for mobile page routing and detailed chart display.

    Parameters:
    -----------
    app : Dash app instance
        The Dash application instance
    chart_id : str
        The ID of the chart to register callbacks for (e.g., 'chart-1')
    chart1_default_period : str
        Default time period to use if none is selected
    detail_figure_generators : dict
        Dict mapping chart_id -> generator function
        Each generator should have signature: func(period, chart_data)
        where chart_data is the deserialized data from CHART_DATA_STORE_ID
    chart_title : dict
        Dict mapping chart_id -> display title for the detail view
    layout_func : function
        Function returning the main dashboard layout
    """
    # define var for each chart
    # PERIOD_BUTTON_TYPE = "period-button"

    # CHART_ID = charts_var[chart_id]["CHART_ID"]

    @app.callback(
        Output("mobile-page-content", "children"),
        Input("mobile-url", "pathname"),
        State(PERIOD_STORE_ID, "data"),  # Must match the store ID in the layout
        State("all-chart-data-store", "data"),
    )
    def display_page(pathname, period_data, all_chart_data):
        """
        Handle URL routing to display different pages based on pathname

        pathname: str - The current URL path
        period_data: Any - Data from the time-period-store (selected period)
        chart_data: dict - Serialized chart data from CHART_DATA_STORE_ID
        """

        if pathname == "/" or pathname is None:
            logger.info(
                "DETAIL DEBUG: Home page path detected, returning to main dashboard"
            )
            # Return empty div since the main layout is handled elsewhere
            return html.Div()

        elif pathname and pathname.startswith("/details/"):
            logger.info(f"DETAIL DEBUG: Details page path detected: {pathname}")
            chart_id = pathname.split("/details/")[-1]
            entry = charts_var.get(chart_id)
            if not entry:
                logger.error(f"DETAIL DEBUG: Chart ID not found: {chart_id}")
                return html.Div()

        chart_factory = entry["chart_factory"]
        chart_title = entry["chart_title"]
        # IMPORTANT: Period data debugging
        if period_data is None:
            logger.fatal(
                f"DETAIL DEBUG: ⚠️ CRITICAL: period_data is None! This indicates a store access issue."
            )

        # Check if we have the expected PERIOD_STORE_ID in the layout
        logger.info(
            f"DETAIL DEBUG: Using PERIOD_STORE_ID={PERIOD_STORE_ID} to access store data"
        )

        # Check for chart_data
        chart_data = all_chart_data.get(f"{chart_id}-data-store", None)
        chart_data_desc = "None or not dict"
        if chart_data and isinstance(chart_data, dict):
            chart_data_desc = f"Dict with keys: {list(chart_data.keys())}"
        logger.info(f"DETAIL DEBUG: chart_data: {chart_data_desc}")

        # --- Generic Detailed View ---
        try:
            if "desktop" in chart_data.keys():
                period = "desktop"
            elif period_data in chart_data.keys():
                period = period_data
            # IMPORTANT: Always check if the period exists in the data
            if chart_data and isinstance(chart_data, dict) and period not in chart_data:
                logger.fatal(
                    f"DETAIL DEBUG: Selected period {period} not found in chart_data! Available periods: {list(chart_data.keys())}"
                )
                # If the selected period doesn't exist in the data, use the first available period
                if chart_data and isinstance(chart_data, dict) and len(chart_data) > 0:
                    period = list(chart_data.keys())[0]
                    logger.warning(
                        f"DETAIL DEBUG: Falling back to first available period: {period}"
                    )
                else:
                    # Last resort fallback
                    period = default_period
                    logger.warning(
                        f"DETAIL DEBUG: Falling back to default period: {period}"
                    )

            logger.info(
                f"DETAIL DEBUG: Final period being used={period}, from store={period_data}, default={default_period}"
            )

            # Deserialize the chart data

            deserialized_chart_data = deserialize_dataframe_dict(chart_data)

            # Check if deserialization was successful
            if deserialized_chart_data is None or (
                isinstance(deserialized_chart_data, dict)
                and "error" in deserialized_chart_data
            ):
                error_msg = (
                    deserialized_chart_data.get("error", "Data deserialization failed")
                    if isinstance(deserialized_chart_data, dict)
                    else "Data deserialization failed"
                )
                logger.fatal(
                    f"Detail view for {chart_id}: Cannot update figure, data unavailable. Msg: {error_msg}"
                )
                # detail_figure = create_generic_placeholder_figure(f"Error: {error_msg}")
                # chart_title = "Data Error"
            # * Table as graph
            if chart_id in table_id:
                logger.info(
                    f"DETAIL DEBUG: Creating table component for {chart_id} with chart_factory"
                )
                logger.info(
                    f"DETAIL DEBUG: Deserialized chart data: {deserialized_chart_data['desktop']}"
                )
                table_component = chart_factory(
                    deserialized_chart_data["desktop"]["all_machine"]
                )
                graph_components = [
                    dbc.Row(
                        dbc.Col(
                            table_component,
                            width=12,
                        ),
                        className="mb-3",
                    )
                ]
            else:
                # Call the generator function with deserialized data
                logger.info(
                    f"DETAIL DEBUG: Creating detail figure for {chart_id} with chart_factory"
                )
                figures = chart_factory(period=period, dfs=deserialized_chart_data)
                logger.info(
                    f"DETAIL DEBUG: Got {len(figures) if isinstance(figures, list) else 1} figures"
                )
                # * Charts as graph
                # Handle multiple figures if returned as array
                graph_components = []
                if isinstance(figures, list):
                    # Create a graph component for each figure in the array
                    for i, fig in enumerate(figures):
                        graph_components.append(
                            dbc.Row(
                                dbc.Col(
                                    dcc.Graph(
                                        id=f"mobile-detail-chart-{chart_id}-{i}",
                                        figure=fig,
                                        style={
                                            "height": "45vh",
                                            "width": "100%",
                                        },
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                        },
                                    ),
                                    width=12,
                                ),
                                className="mb-5",  # Add  bottom margin between charts
                            )
                        )
                else:
                    # Single figure case
                    graph_components = [
                        dbc.Row(
                            dbc.Col(
                                dcc.Graph(
                                    id=f"mobile-detail-chart-{chart_id}",
                                    figure=figures,
                                    style={
                                        "height": "80vh",
                                        "width": "100%",
                                    },
                                    config={
                                        "displayModeBar": False,
                                        "responsive": True,
                                    },
                                ),
                                width=12,
                            ),
                            className="mb-3",  # Add bottom margin
                        )
                    ]

            # Wrap all graph components in a scrollable container
            graphs_container = html.Div(
                children=graph_components,
                style={
                    "overflowY": "auto",
                    "maxHeight": "90vh",  # Limit height to ensure scrollability
                    "padding": "5px",
                },
            )

            return_layout = html.Div(
                id=f"mobile-detail-wrapper-{chart_id}",  # Dynamic ID
                style={
                    "width": "100vw",
                    "height": "100vh",
                    "overflowY": "auto",  # Ensure vertical scrolling is enabled
                    "overflowX": "hidden",  # Prevent horizontal scrolling
                    "position": "relative",
                    "backgroundColor": "#000000",
                    "zIndex": 1000,  # Ensure it's on top of everything
                },
                children=[
                    dbc.Container(
                        id=f"mobile-rotated-detail-content-{chart_id}",  # Dynamic ID
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Link(
                                            "Back",
                                            href="/",
                                            className="btn btn-secondary btn-sm",
                                        ),
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        html.H4(
                                            chart_title,
                                            className="text-white text-center",
                                        ),
                                        width=True,
                                    ),
                                ],
                                align="center",
                                className="mb-2",
                            ),
                            # Insert the scrollable graphs container instead of individual components
                            graphs_container,
                        ],
                        fluid=True,
                    )
                ],
            )
            logger.info(f"DETAIL DEBUG: Returning detail page layout")
            return return_layout
        except Exception as e:
            logger.error(
                f"DETAIL DEBUG: Error generating detailed view for chart {chart_id}: {e}",
                exc_info=True,
            )
            # Generic Error Page
            return html.Div(
                id="mobile-error-wrapper",
                style={
                    "width": "100vw",
                    "height": "100vh",
                    "overflowY": "auto",  # Ensure vertical scrolling is enabled
                    "overflowX": "hidden",  # Prevent horizontal scrolling
                    "backgroundColor": "#000",
                    "zIndex": 1000,  # Ensure it's on top of everything
                },
                children=[
                    dbc.Container(
                        [
                            html.H4(
                                "Error Loading Detail View", className="text-danger"
                            ),
                            html.Pre(str(e), className="text-white"),
                            dcc.Link(
                                "Back to Dashboard",
                                href="/",
                                className="btn btn-secondary",
                            ),
                        ],
                    )
                ],
            )

    # logger.info(f"Mobile page callbacks registered for chart {chart_id}.")
