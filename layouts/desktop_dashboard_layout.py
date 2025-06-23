import dash_bootstrap_components as dbc
from dash import html, dcc
from PlotCharts.PlotChart_MachineUsage import create_chart1_layout
from PlotCharts.PlotChart_MachineStatus import create_chart2_layout
from PlotCharts.PlotChart_chart3 import create_chart3_layout
from PlotCharts.PlotChart_chart4 import create_chart4_layout
from PlotCharts.PlotChart_chart5 import create_chart5_layout
from PlotCharts.PlotChart_chart6 import create_chart6_layout
from Database.serialize_df import serialize_dataframe_dict
from layouts.create_buttons import create_period_button, create_theme_buttons

# Note: Figures are passed from mobile_app.py


def create_desktop_layout(
    initial_charts_data: dict,
    color_theme,
    lang,
    default_period: str = "今天",
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
            "width": "100%",
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
                id="desktop-content",
                fluid=True,
                className="px-2 py-3",
                children=[
                    # dbc.Row(
                    #     dbc.Col(
                    #         html.H2(
                    #             "Desktop Dashboard",
                    #             className="text-center my-3",
                    #             style={"fontSize": "calc(1.3rem + 0.6vw)"},
                    #         ),
                    #         width=12,
                    #     )
                    # ),
                    dbc.Row(
                        [
                            dbc.Col(
                                # Call the imported button creation function
                                create_period_button(periods=periods),
                                width=4,  # Align with first chart column
                                className="d-flex align-items-center",
                            ),
                            dbc.Col(width=4),  # Empty space in middle
                            dbc.Col(
                                # Add color theme buttons on the right
                                create_theme_buttons(),
                                width=4,
                                className="d-flex justify-content-end align-items-center",  # Align to the right
                            ),
                        ],
                        className="mb-2 g-2",
                    ),
                    # Row 1 (Charts 1-3)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    create_chart1_layout(
                                        default_period=default_period,
                                        dfs=initial_charts_data["chart-1-data-store"],
                                        mobile=False,
                                        chart_id="chart-1",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    create_chart2_layout(
                                        dfs=initial_charts_data["chart-2-data-store"],
                                        mobile=False,
                                        chart_id="chart-2",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    create_chart3_layout(
                                        default_period=default_period,
                                        dfs=initial_charts_data["chart-3-data-store"],
                                        mobile=False,
                                        chart_id="chart-3",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                        ],
                        className="mb-1 g-2",
                        align="stretch",
                    ),
                    # Row 2 (Charts 4-6)
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    create_chart4_layout(
                                        default_period=default_period,
                                        dfs=initial_charts_data["chart-4-data-store"],
                                        mobile=False,
                                        chart_id="chart-4",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    create_chart5_layout(
                                        default_period="24_hrs",
                                        dfs=initial_charts_data["chart-5-data-store"],
                                        mobile=False,
                                        chart_id="chart-5",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    create_chart6_layout(
                                        default_period=default_period,
                                        dfs=initial_charts_data["chart-6-data-store"],
                                        mobile=False,
                                        chart_id="chart-6",
                                    ),
                                    body=True,
                                    style={
                                        "height": "40vh",
                                        "backgroundColor": "transparent",
                                    },
                                ),
                                width=4,
                            ),
                        ],
                        className="mb-1 g-2",
                        align="stretch",
                    ),
                    # Placeholder for potential future updates or controls
                    html.Div(id="mobile-dynamic-content", className="text-center"),
                    dcc.Interval(
                        id="mobile-interval", interval=60 * 1000, n_intervals=0
                    ),
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
                    dcc.Store(
                        id="chart5-timeframe-store",
                        data="24_hrs",
                        storage_type="session",
                    ),
                ],
                style={
                    "width": "100%",
                    "height": "100%",
                    "padding": "clamp(0.5rem, 2vw, 2rem)",
                    "maxWidth": "100%",
                },
            ),
        ],
    )
