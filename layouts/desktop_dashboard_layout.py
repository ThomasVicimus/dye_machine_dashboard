import dash_bootstrap_components as dbc
from dash import html, dcc
from PlotCharts.PlotChart_MachineUsage import create_chart1_layout
from Database.serialize_df import serialize_dataframe_dict
from layouts.create_buttons import create_period_button, create_theme_buttons

# Note: Figures are passed from mobile_app.py


def create_desktop_layout(
    initial_charts_data: dict,
    color_theme,
    lang,
    default_period: str = "今日",
):
    """Creates the main mobile dashboard layout structure with clickable charts.

    Args:
        initial_charts (dict): Dictionary mapping chart IDs to initial figure objects.
        initial_chart_data (dict): Dictionary containing the initially fetched data for charts.
        color_theme: The color theme setting.
        lang: The language setting.
    """
    periods = initial_charts_data["chart1-data-store"].keys()
    # charts = {
    #     "mobile-chart-1": initial_charts_layout["machine_usage"],
    #     "mobile-chart-2": initial_charts_layout["machine_usage"],
    #     "mobile-chart-3": initial_charts_layout["machine_usage"],
    #     "mobile-chart-4": initial_charts_layout["machine_usage"],
    #     "mobile-chart-5": initial_charts_layout["machine_usage"],
    #     "mobile-chart-6": initial_charts_layout["machine_usage"],
    # }

    # def create_chart_column(chart_id, figure):
    #     """Helper to create a Bootstrap column containing a clickable chart graph."""
    #     graph_component = dcc.Graph(
    #         id=chart_id,
    #         figure=figure,
    #         style={"height": "20vh", "width": "95%"},
    #         config={"displayModeBar": False},
    #     )
    #     return dbc.Col(
    #         dcc.Link(
    #             graph_component,
    #             href=f"/details/{chart_id}",  # Link using the chart ID
    #             id=f"link-{chart_id}",
    #             style={
    #                 "display": "block",
    #                 "height": "100%",
    #                 "width": "100%",
    #             },  # Ensure link covers graph
    #         ),
    #         width=4,
    #         className="p-0",
    #     )

    return html.Div(
        id="dashboard-content",
        style={
            # "width": "100vw",
            # "height": "100vh",
            "overflowY": "auto",
            "position": "relative",
            "backgroundColor": "#202020",
        },
        children=[
            # Add URL location tracking component
            dcc.Location(id="mobile-url", refresh=False),
            # Add the container for page content (used by detail_page_callbacks.py)
            html.Div(id="mobile-page-content"),
            # Add theme store for theme switching
            dcc.Store(id="theme-store", data=color_theme),
            dbc.Container(
                id="desktop-content",
                # id="mobile-rotated-content",
                children=[
                    dbc.Row(
                        dbc.Col(
                            html.H2(
                                "Desktop Dashboard",
                                className="text-center my-3",
                            ),
                            width=12,
                        )
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                # Call the imported button creation function
                                create_period_button(periods=periods),
                                width=4,  # Align with first chart column
                            ),
                            dbc.Col(width=4),  # Empty space in middle
                            dbc.Col(
                                # Add color theme buttons on the right
                                create_theme_buttons(),
                                width=4,
                                className="d-flex justify-content-end",  # Align to the right
                            ),
                        ],
                        className="mb-2",
                    ),
                    # Row 1 (Charts 1-3)
                    dbc.Row(
                        [
                            create_chart1_layout(
                                default_period=default_period,
                                dfs=initial_charts_data["chart1-data-store"],
                                mobile=False,
                                chart_id="chart-1",
                            ),
                            create_chart1_layout(
                                default_period=default_period,
                                dfs=initial_charts_data["chart1-data-store"],
                                mobile=False,
                                chart_id="chart-2",
                            ),
                            create_chart1_layout(
                                default_period=default_period,
                                dfs=initial_charts_data["chart1-data-store"],
                                mobile=False,
                                chart_id="chart-3",
                            ),
                        ],
                        className="mb-1 g-0",
                        align="stretch",
                    ),
                    # Row 2 (Charts 4-6)
                    # dbc.Row(
                    #     [
                    #         create_chart_column(cid, fig)
                    #         for cid, fig in list(charts.items())[3:]
                    #     ],
                    #     className="mb-1 g-0",
                    #     align="stretch",
                    # ),
                    # Placeholder for potential future updates or controls
                    html.Div(id="mobile-dynamic-content", className="text-center"),
                    dcc.Interval(
                        id="mobile-interval", interval=60 * 1000, n_intervals=0
                    ),
                    # Add the data store here and populate with initial data
                    dcc.Store(
                        id="chart1-data-store",
                        data=serialize_dataframe_dict(
                            initial_charts_data["chart1-data-store"]
                        ),
                    ),
                    dcc.Store(
                        id="time-period-store",
                        data=default_period,
                        storage_type="session",
                    ),
                ],
                fluid=True,
                style={"max-width": "1920px", "padding": "20px"},
                # style={
                #     "transform": "rotate(90deg)",
                #     "transformOrigin": "top left",
                #     "width": "100vh",
                #     "height": "100vw",
                #     "position": "absolute",
                #     "top": "0",
                #     "left": "100%",
                #     "padding": "10px",
                #     "display": "flex",
                #     "flexDirection": "column",
                #     "marginBottom": "5vh",
                # },
            ),
        ],
    )
