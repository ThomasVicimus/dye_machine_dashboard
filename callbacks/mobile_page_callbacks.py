import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State

# Assumes CHART1_PERIOD_STORE_ID is defined in mobile_app.py and passed correctly
# Assumes chart_factory, chart1_default_period, load_data_func, layout_func are passed

logger = logging.getLogger(__name__)


def register_mobile_page_callbacks(
    app,
    chart_factory,
    chart1_default_period,
    chart1_period_store_id,
    load_data_func,  # Function to load data for detailed view (e.g., get_MachineUsage_data)
    layout_func,  # Function to generate main layout (create_main_dashboard_layout)
):
    """Registers callbacks for mobile page routing and content display."""

    @app.callback(
        Output("mobile-page-content", "children"),
        Input("mobile-url", "pathname"),
        State(chart1_period_store_id, "data"),  # Get the currently selected period
    )
    def display_page(pathname, chart1_period_data):
        if pathname == "/details/machine-usage":
            # --- Detailed Machine Usage View ---
            try:
                # Determine the period to use
                period = (
                    chart1_period_data if chart1_period_data else chart1_default_period
                )
                logger.info(f"Loading detailed view for period: {period}")

                # Load data required for the detailed chart using the passed function
                # Assumes load_data_func connects/closes DB if needed
                dfs = load_data_func(period=period)

                # Generate the detailed figure
                detailed_figure = chart_factory.create_machine_usage_chart_mobile_all_machine(
                    period=period,
                    dfs=dfs,
                    # Add other specific parameters if needed
                )

                # Layout for the detailed page (needs rotation wrapper)
                return html.Div(
                    id="mobile-detail-wrapper",
                    style={
                        "width": "100vw",
                        "height": "100vh",
                        "overflowY": "auto",
                        "position": "relative",
                        "backgroundColor": "#000000",
                    },
                    children=[
                        dbc.Container(
                            id="mobile-rotated-detail-content",
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
                                                "Detailed Usage",
                                                className="text-white text-center",
                                            ),
                                            width=True,
                                        ),
                                    ],
                                    align="center",
                                    className="mb-2",
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        dcc.Graph(
                                            id="mobile-detail-chart",
                                            figure=detailed_figure,
                                            style={
                                                "height": "80vh",
                                                "width": "100%",
                                            },
                                            config={"displayModeBar": True},
                                        ),
                                        width=12,
                                    )
                                ),
                            ],
                            fluid=True,
                            style={
                                "transform": "rotate(90deg)",
                                "transformOrigin": "top left",
                                "width": "100vh",
                                "height": "100vw",
                                "position": "absolute",
                                "top": "0",
                                "left": "100%",
                                "padding": "15px",
                                "display": "flex",
                                "flexDirection": "column",
                            },
                        )
                    ],
                )
            except Exception as e:
                logger.error(f"Error generating detailed view: {e}", exc_info=True)
                return html.Div(
                    id="mobile-error-wrapper",
                    style={
                        "width": "100vw",
                        "height": "100vh",
                        "backgroundColor": "#000",
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
                            },
                        )
                    ],
                )
        elif pathname == "/" or pathname is None:
            # --- Main Dashboard View ---
            # Call the passed layout function
            # We need the initial figures again here, which might be tricky.
            # Re-fetching or passing them to register_mobile_page_callbacks is needed.
            # For now, let's assume layout_func can handle this or we adjust later.
            # Let's modify layout_func call later in mobile_app.py to include figures.
            return layout_func()
        else:
            # --- 404 Not Found Page ---
            return html.Div(
                id="mobile-404-wrapper",
                style={"width": "100vw", "height": "100vh", "backgroundColor": "#000"},
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
                        },
                    )
                ],
            )

    logger.info("Mobile page callbacks registered.")
