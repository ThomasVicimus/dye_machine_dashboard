import dash_bootstrap_components as dbc
from dash import html, dcc

# Note: Figures are passed from mobile_app.py


def create_main_dashboard_layout(initial_charts: dict, color_theme, lang):
    """Creates the main mobile dashboard layout structure with clickable charts."""

    charts = {
        "mobile-chart-1": initial_charts["machine_usage"],
        "mobile-chart-2": initial_charts["machine_usage"],
        "mobile-chart-3": initial_charts["machine_usage"],
        "mobile-chart-4": initial_charts["machine_usage"],
        "mobile-chart-5": initial_charts["machine_usage"],
        "mobile-chart-6": initial_charts["machine_usage"],
    }

    def create_chart_column(chart_id, figure):
        """Helper to create a Bootstrap column containing a clickable chart graph."""
        graph_component = dcc.Graph(
            id=chart_id,
            figure=figure,
            style={"height": "20vh", "width": "95%"},
            config={"displayModeBar": False},
        )
        return dbc.Col(
            dcc.Link(
                graph_component,
                href=f"/details/{chart_id}",  # Link using the chart ID
                id=f"link-{chart_id}",
                style={
                    "display": "block",
                    "height": "100%",
                    "width": "100%",
                },  # Ensure link covers graph
            ),
            width=4,
            className="p-0",
        )

    return html.Div(
        id="mobile-wrapper",
        style={
            "width": "100vw",
            "height": "100vh",
            "overflowY": "auto",
            "position": "relative",
            "backgroundColor": "#000000",
        },
        children=[
            dbc.Container(
                id="mobile-rotated-content",
                children=[
                    dbc.Row(
                        dbc.Col(
                            html.H2(
                                "Mobile Dashboard",
                                className="text-center pt-1 pb-0 text-white",
                            ),
                            width=12,
                        )
                    ),
                    # Row 1 (Charts 1-3)
                    dbc.Row(
                        [
                            create_chart_column(cid, fig)
                            for cid, fig in list(charts.items())[:3]
                        ],
                        className="mb-1 g-0",
                        align="stretch",
                    ),
                    # Row 2 (Charts 4-6)
                    dbc.Row(
                        [
                            create_chart_column(cid, fig)
                            for cid, fig in list(charts.items())[3:]
                        ],
                        className="mb-1 g-0",
                        align="stretch",
                    ),
                    # Placeholder for potential future updates or controls
                    html.Div(
                        id="mobile-dynamic-content", className="text-white text-center"
                    ),
                    dcc.Interval(
                        id="mobile-interval", interval=60 * 1000, n_intervals=0
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
                    "padding": "10px",
                    "display": "flex",
                    "flexDirection": "column",
                    "marginBottom": "5vh",
                },
            )
        ],
    )
