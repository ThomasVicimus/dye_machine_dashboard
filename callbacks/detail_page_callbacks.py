import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State
import plotly.graph_objects as go  # Import go for placeholder
from ChartFactory.chart_factory_MachineUasge import MachineUsageChart
from dash.dependencies import ALL
from dash import callback_context
from Database.serialize_df import deserialize_dataframe_dict

# Assumes CHART1_PERIOD_STORE_ID is defined and passed
# Assumes detail_figure_generators (dict mapping chart_id -> function(period)) is passed
# Assumes chart_titles (dict mapping chart_id -> str) is passed
# Assumes layout_func (function returning main layout) is passed

logger = logging.getLogger(__name__)


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


def register_mobile_page_callbacks(
    app,
    chart_id,
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
    chart_titles : dict
        Dict mapping chart_id -> display title for the detail view
    layout_func : function
        Function returning the main dashboard layout
    """
    # define var for each chart
    PERIOD_BUTTON_TYPE = "period-button"
    PERIOD_STORE_ID = (
        "time-period-store"  # Ensure this matches the ID in mobile_dashboard_layout.py
    )
    charts_var = {
        "chart-1": {
            "CHART_ID": "chart-1",
            "CHART_DATA_STORE_ID": "chart1-data-store",
            "chart_factory": MachineUsageChart(
                {}, lang=lang
            ),  # Create factory instance for callbacks
            "chart_titles": "Machine Usage",
        },
        # "chart2": {
        #     "CHART_ID": "chart-2",
        #     "PERIOD_STORE_ID": "selected-period-store-chart2",
        #     "CHART_DATA_STORE_ID": "chart2-data-store",
        #     "PERIOD_BUTTON_TYPE": "period-button",
        # },
    }

    CHART_ID = charts_var[chart_id]["CHART_ID"]
    CHART_DATA_STORE_ID = charts_var[chart_id]["CHART_DATA_STORE_ID"]
    chart_factory = charts_var[chart_id]["chart_factory"]
    chart_titles = charts_var[chart_id]["chart_titles"]

    @app.callback(
        Output("mobile-page-content", "children"),
        Input("mobile-url", "pathname"),
        State(PERIOD_STORE_ID, "data"),  # Must match the store ID in the layout
        State(CHART_DATA_STORE_ID, "data"),
    )
    def display_page(pathname, period_data, chart_data):
        """
        Handle URL routing to display different pages based on pathname

        pathname: str - The current URL path
        period_data: Any - Data from the time-period-store (selected period)
        chart_data: dict - Serialized chart data from CHART_DATA_STORE_ID
        """
        logger.info(f"DETAIL DEBUG: callback triggered with pathname={pathname}")
        logger.info(
            f"DETAIL DEBUG: PERIOD_STORE_ID='{PERIOD_STORE_ID}', CHART_DATA_STORE_ID='{CHART_DATA_STORE_ID}'"
        )
        logger.info(f"DETAIL DEBUG: Using chart_id={chart_id} for this callback")

        # IMPORTANT: Period data debugging
        if period_data is None:
            logger.warning(
                f"DETAIL DEBUG: ⚠️ CRITICAL: period_data is None! This indicates a store access issue."
            )
        else:
            logger.info(
                f"DETAIL DEBUG: period_data from store={period_data} (type={type(period_data)})"
            )

        # Check if we have the expected PERIOD_STORE_ID in the layout
        logger.info(
            f"DETAIL DEBUG: Using PERIOD_STORE_ID={PERIOD_STORE_ID} to access store data"
        )

        # Check for chart_data
        chart_data_desc = "None or not dict"
        if chart_data and isinstance(chart_data, dict):
            chart_data_desc = f"Dict with keys: {list(chart_data.keys())}"
        logger.info(f"DETAIL DEBUG: chart_data: {chart_data_desc}")

        if pathname and pathname.startswith("/details/"):
            logger.info(f"DETAIL DEBUG: Detected details URL pattern: {pathname}")
            # --- Generic Detailed View ---
            try:
                # Extract chart_id from URL (e.g., /details/chart-1 -> chart-1)
                url_chart_id = pathname.split("/")[-1]
                logger.info(f"DETAIL DEBUG: Extracted url_chart_id={url_chart_id}")

                # Always use the current chart_id for this callback
                # The URL may contain any chart ID, but we'll use the one registered for this callback
                detail_chart_id = chart_id
                logger.info(
                    f"DETAIL DEBUG: Using registered chart_id={detail_chart_id} for display"
                )

                if not url_chart_id:
                    raise ValueError("Chart ID missing in URL")

                # Determine the period to use
                if period_data is None:
                    logger.warning(
                        f"DETAIL DEBUG: period_data is None! Falling back to default_period={default_period}"
                    )
                    period = default_period
                else:
                    logger.info(f"DETAIL DEBUG: Using selected period: {period_data}")
                    period = period_data

                # IMPORTANT: Always check if the period exists in the data
                if (
                    chart_data
                    and isinstance(chart_data, dict)
                    and period not in chart_data
                ):
                    logger.warning(
                        f"DETAIL DEBUG: Selected period {period} not found in chart_data! Available periods: {list(chart_data.keys())}"
                    )
                    # If the selected period doesn't exist in the data, use the first available period
                    if (
                        chart_data
                        and isinstance(chart_data, dict)
                        and len(chart_data) > 0
                    ):
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

                # Log period data to understand what's happening
                logger.info(f"DETAIL DEBUG: PERIOD_STORE_ID={PERIOD_STORE_ID}")
                logger.info(
                    f"DETAIL DEBUG: period_data type={type(period_data)}, value={period_data}"
                )

                logger.info(
                    f"Loading detail view for chart {chart_id}, period: {period}"
                )

                # Deserialize the chart data
                logger.info(
                    f"DETAIL DEBUG: Chart data type before deserialization: {type(chart_data)}"
                )
                logger.info(f"DETAIL DEBUG: Chart data is None? {chart_data is None}")

                deserialized_chart_data = deserialize_dataframe_dict(chart_data)
                logger.info(
                    f"DETAIL DEBUG: Deserialization result type: {type(deserialized_chart_data)}"
                )

                # Check if deserialization was successful
                if deserialized_chart_data is None or (
                    isinstance(deserialized_chart_data, dict)
                    and "error" in deserialized_chart_data
                ):
                    error_msg = (
                        deserialized_chart_data.get(
                            "error", "Data deserialization failed"
                        )
                        if isinstance(deserialized_chart_data, dict)
                        else "Data deserialization failed"
                    )
                    logger.warning(
                        f"DETAIL DEBUG: Detail view for {chart_id}: Cannot update figure, data unavailable. Msg: {error_msg}"
                    )
                    detail_figure = create_generic_placeholder_figure(
                        f"Error: {error_msg}"
                    )
                    detail_title = "Data Error"
                else:
                    # Call the generator function with deserialized data
                    logger.info(
                        f"DETAIL DEBUG: Creating detail figure for {chart_id} with chart_factory"
                    )
                    figures = (
                        chart_factory.create_machine_usage_chart_mobile_all_machine(
                            period=period, dfs=deserialized_chart_data
                        )
                    )
                    logger.info(
                        f"DETAIL DEBUG: Got {len(figures) if isinstance(figures, list) else 1} figures"
                    )
                    detail_title = chart_titles
                    logger.info(f"DETAIL DEBUG: Figure created, title={detail_title}")

                # Generic layout for the detailed page (needs rotation wrapper)
                logger.info(f"DETAIL DEBUG: Building detail page layout")

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
                                            "height": "40vh",
                                            "width": "100%",
                                        },
                                        config={"displayModeBar": False},
                                    ),
                                    width=12,
                                ),
                                className="mb-3",  # Add bottom margin between charts
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
                                    config={"displayModeBar": False},
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
                                                detail_title,
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
                            style={
                                "transform": "rotate(90deg)",
                                "transformOrigin": "top left",
                                "width": "100vh",  # This matches the height of the viewport in the rotated view
                                "height": "100vw",  # This matches the width of the viewport in the rotated view
                                "position": "absolute",
                                "top": "0",
                                "left": "100%",
                                "padding": "15px",
                                "display": "flex",
                                "flexDirection": "column",
                                "overflowY": "auto",  # Enable scrolling on the rotated content
                                "backgroundColor": "#000000",  # Make sure container background is solid
                            },
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
                            style={
                                "transform": "rotate(90deg)",
                                "transformOrigin": "top left",
                                "width": "100vh",
                                "height": "100vw",
                                "position": "absolute",
                                "top": "0",
                                "left": "100%",
                                "padding": "15px",
                                "color": "white",
                                "overflowY": "auto",  # Enable scrolling on the rotated content
                                "backgroundColor": "#000000",  # Make sure container background is solid
                            },
                        )
                    ],
                )
        else:
            logger.warning(
                f"DETAIL DEBUG: Pathname did not match /details/ pattern: {pathname}"
            )
            # Check if this is the home page
            if pathname == "/" or pathname is None:
                logger.info(
                    "DETAIL DEBUG: Home page path detected, returning to main dashboard"
                )
                # Return empty div since the main layout is handled elsewhere
                return html.Div()
            else:
                # --- 404 Not Found Page ---
                logger.warning(f"Pathname not found: {pathname}")
                return html.Div(
                    id="mobile-404-wrapper",
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
                                html.H1("404 - Not Found", className="text-danger"),
                                dcc.Link("Go to Dashboard", href="/"),
                            ],
                            style={
                                "transform": "rotate(90deg)",
                                "transformOrigin": "top left",
                                "width": "100vh",
                                "height": "100vw",
                                "position": "absolute",
                                "top": "0",
                                "left": "100%",
                                "padding": "15px",
                                "color": "white",
                                "overflowY": "auto",  # Enable scrolling on the rotated content
                                "backgroundColor": "#000000",  # Make sure container background is solid
                            },
                        )
                    ],
                )

    logger.info(f"Mobile page callbacks registered for chart {CHART_ID}.")
