import dash_bootstrap_components as dbc
from dash import html, dcc

# Note: create_chart1_layout is imported in mobile_app.py and passed here.
# initial_chart1_figure and placeholder_chart_figure are also passed.


def create_main_dashboard_layout(
    create_chart1_layout_func, initial_chart1_fig, placeholder_fig
):
    """Creates the main mobile dashboard layout structure."""
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
                            # Pass href to create_chart1_layout
                            create_chart1_layout_func(
                                initial_chart1_fig,
                                mobile=True,
                                href="/details/machine-usage",  # Link to the detail page
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="mobile-chart-2",
                                    figure=placeholder_fig,
                                    style={"height": "20vh", "width": "95%"},
                                    config={"displayModeBar": False},  # Added config
                                ),
                                width=4,
                                className="p-0",
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="mobile-chart-3",
                                    figure=placeholder_fig,
                                    style={"height": "20vh", "width": "95%"},
                                    config={"displayModeBar": False},  # Added config
                                ),
                                width=4,
                                className="p-0",
                            ),
                        ],
                        className="mb-1 g-0",
                        align="stretch",
                    ),
                    # Row 2 (Charts 4-6)
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    id="mobile-chart-4",
                                    figure=placeholder_fig,
                                    style={"height": "20vh", "width": "95%"},
                                    config={"displayModeBar": False},  # Added config
                                ),
                                width=4,
                                className="p-0",
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="mobile-chart-5",
                                    figure=placeholder_fig,
                                    style={"height": "20vh", "width": "95%"},
                                    config={"displayModeBar": False},  # Added config
                                ),
                                width=4,
                                className="p-0",
                            ),
                            dbc.Col(
                                dcc.Graph(
                                    id="mobile-chart-6",
                                    figure=placeholder_fig,
                                    style={"height": "20vh", "width": "95%"},
                                    config={"displayModeBar": False},  # Added config
                                ),
                                width=4,
                                className="p-0",
                            ),
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
