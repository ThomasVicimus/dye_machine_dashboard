import logging
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State
import plotly.graph_objects as go  # Import go for placeholder

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
    chart1_default_period,
    chart1_period_store_id,
    detail_figure_generators: dict,  # e.g., {'mobile-chart-1': func1, ...}
    chart_titles: dict,  # e.g., {'mobile-chart-1': 'Details Chart 1', ...}
    layout_func,
):
    """Registers callbacks for mobile page routing and generic content display."""

    @app.callback(
        Output("mobile-page-content", "children"),
        Input("mobile-url", "pathname"),
        State(chart1_period_store_id, "data"),
    )
    def display_page(pathname, chart1_period_data):

        if pathname and pathname.startswith("/details/"):
            # --- Generic Detailed View ---
            try:
                # Extract chart_id from URL (e.g., /details/mobile-chart-1 -> mobile-chart-1)
                chart_id = pathname.split("/")[-1]

                if not chart_id:
                    raise ValueError("Chart ID missing in URL")

                # Determine the period to use
                period = (
                    chart1_period_data if chart1_period_data else chart1_default_period
                )
                logger.info(f"Loading detail view for {chart_id}, period: {period}")

                # Get the specific figure generator function for this chart_id
                figure_generator = detail_figure_generators.get(chart_id)

                if figure_generator:
                    # Call the generator function (it should handle data fetching)
                    detail_figure = figure_generator(period=period)
                    detail_title = chart_titles.get(
                        chart_id, "Detail View"
                    )  # Get title
                else:
                    logger.warning(
                        f"No detail figure generator found for chart_id: {chart_id}"
                    )
                    detail_figure = create_generic_placeholder_figure(
                        f"No detail view for {chart_id}"
                    )
                    detail_title = "Detail View Unavailable"

                # Generic layout for the detailed page (needs rotation wrapper)
                return html.Div(
                    id=f"mobile-detail-wrapper-{chart_id}",  # Dynamic ID
                    style={
                        "width": "100vw",
                        "height": "100vh",
                        "overflowY": "auto",
                        "position": "relative",
                        "backgroundColor": "#000000",
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
                                dbc.Row(
                                    dbc.Col(
                                        dcc.Graph(
                                            id=f"mobile-detail-chart-{chart_id}",  # Dynamic ID
                                            figure=detail_figure,
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
                chart_id_info = (
                    f" (Chart ID: {chart_id})" if "chart_id" in locals() else ""
                )
                logger.error(
                    f"Error generating detailed view{chart_id_info}: {e}", exc_info=True
                )
                # Generic Error Page
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
            logger.debug("Displaying main dashboard layout.")
            return layout_func()
        else:
            # --- 404 Not Found Page ---
            logger.warning(f"Pathname not found: {pathname}")
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
