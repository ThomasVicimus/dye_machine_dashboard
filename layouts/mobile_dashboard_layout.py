import dash_bootstrap_components as dbc
from dash import html, dcc
from PlotCharts.PlotChart_MachineUsage import create_chart1_layout
from PlotCharts.PlotChart_MachineStatus import create_chart2_layout
from Database.serialize_df import serialize_dataframe_dict
from layouts.create_buttons import create_period_button, create_theme_buttons

# Note: Figures are passed from mobile_app.py


def create_mobile_layout(
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
    periods = initial_charts_data["chart-1-data-store"].keys()
    serialized_initial_charts_data = {
        key: serialize_dataframe_dict(df) for key, df in initial_charts_data.items()
    }

    return html.Div(
        id="dashboard-content",
        style={
            "width": "100vw",
            "height": "100vh",
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
                id="mobile-rotated-content",
                children=[
                    dbc.Row(
                        dbc.Col(
                            html.H2(
                                "Mobile Dashboard",
                                className="text-center pt-1 pb-0",
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
                                dfs=initial_charts_data["chart-1-data-store"],
                                mobile=True,
                                chart_id="chart-1",
                            ),
                            create_chart2_layout(
                                dfs=initial_charts_data["chart-2-data-store"],
                                mobile=True,
                                chart_id="chart-2",
                            ),
                            create_chart1_layout(
                                default_period=default_period,
                                dfs=initial_charts_data["chart-1-data-store"],
                                mobile=True,
                                chart_id="chart-3",
                            ),
                        ],
                        className="mb-1 g-0",
                        align="stretch",
                        style={"height": "20vh"},
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
                    # TODOL Json serialize the data store
                    # Add the data store here and populate with initial data
                    dcc.Store(
                        id="all-chart-data-store",
                        data=serialized_initial_charts_data,
                    ),
                    dcc.Store(
                        id="time-period-store",
                        data=default_period,
                        storage_type="session",
                    ),
                ],
                fluid=True,
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
