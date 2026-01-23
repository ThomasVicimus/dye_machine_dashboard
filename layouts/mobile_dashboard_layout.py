import dash_bootstrap_components as dbc
from dash import html, dcc
from PlotCharts.PlotChart_MachineUsage import create_chart1_layout
from PlotCharts.PlotChart_MachineStatus import create_chart2_layout
from PlotCharts.PlotChart_chart3 import create_chart3_layout
from PlotCharts.PlotChart_chart4 import create_chart4_layout
from PlotCharts.PlotChart_chart5 import create_chart5_layout
from PlotCharts.PlotChart_chart6 import create_chart6_layout
from Database.serialize_df import serialize_dataframe_dict

# from layouts.create_buttons import create_period_button, create_theme_buttons
from layouts.create_buttons import (
    create_main_page_turner_buttons,
    create_combined_control_row,
)
from function.dashboard_config import (
    get_data_refresh_interval,
    get_chart5_default_timeframe,
    get_lane_count,
)

# Note: Figures are passed from mobile_app.py


def create_mobile_layout(
    initial_charts_data: dict,
    color_theme,
    lang,
    default_period: str = "今天",
):
    """Creates the main mobile dashboard layout structure with clickable charts.

    Args:
        initial_charts_data (dict): Dict of initial chart datasets keyed by store id
            (e.g. "chart-1-data-store"). Values are nested dicts of DataFrames.
        color_theme: Theme setting (e.g. "black", "dark_blue")
        lang: Language setting (e.g. "zh_cn")
        default_period: Initial selected period key (e.g. "今天")
    """
    # Get values from config
    REFRESH_INTERVAL = get_data_refresh_interval()
    CHART5_DEFAULT_TIMEFRAME = get_chart5_default_timeframe()

    # Period options are derived from chart-1 periods (the global period selector contract)
    periods = list(initial_charts_data["chart-1-data-store"].keys())
    serialized_initial_charts_data = {
        key: serialize_dataframe_dict(df) for key, df in initial_charts_data.items()
    }

    # Sticky control-row style (also used by a callback to hide it on detail pages)
    MAIN_CONTROLS_ROW_STYLE = {
        "position": "sticky",
        "top": "0",
        "zIndex": "1020",
        "backgroundColor": "#202020",
        "paddingTop": "5px",
        "paddingBottom": "5px",
    }

    return html.Div(
        id="dashboard-content",
        style={
            "width": "100vw",
            "height": "100vh",
            # Prevent "double scroll" when detail overlays are rendered.
            # The dashboard itself scrolls inside `mobile-dashboard-page`.
            "overflow": "hidden",
            "position": "relative",
            "backgroundColor": "#202020",
        },
        children=[
            # Add URL location tracking component
            dcc.Location(id="mobile-url", refresh=False),
            # Add theme store for theme switching
            dcc.Store(id="theme-store", data=color_theme),
            # Data stores used by callbacks/detail routing.
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
                data=CHART5_DEFAULT_TIMEFRAME,
                storage_type="session",
            ),
            dcc.Store(
                id="main-page-index-store",
                data=0,
                storage_type="session",
            ),
            # Detail page content (populated by `callbacks/detail_page_callbacks.py`).
            # This is intentionally separate from the dashboard page container so the
            # detail view can act like a full-screen overlay without fighting scroll.
            html.Div(id="mobile-page-content"),
            # Main dashboard page
            html.Div(
                id="mobile-dashboard-page",
                style={
                    "height": "100%",
                    "width": "100%",
                    "overflowY": "auto",
                },
                children=[
                    dbc.Container(
                        id="mobile-rotated-content",
                        children=[
                            # dbc.Row(
                            #     dbc.Col(
                            #         html.H2(
                            #             "Mobile Dashboard",
                            #             className="text-center pt-1 pb-0",
                            #         ),
                            #         width=12,
                            #     )
                            # ),
                            # Pagination row for mobile
                            # Combined Control Row (Sticky)
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        create_combined_control_row(
                                            periods=periods,
                                            selected_period=default_period,
                                            current_page=0,
                                            total_pages=1,
                                        ),
                                        width=12,
                                    ),
                                ],
                                id="mobile-main-controls-row",
                                className="mb-1",
                                style=MAIN_CONTROLS_ROW_STYLE,
                            ),
                            # * Buttons removed for now
                            # Row 1 (Charts 1-3)
                            html.Div(
                                className="mobile-row-page",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart1_layout(
                                                        default_period=default_period,
                                                        dfs=initial_charts_data[
                                                            "chart-1-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-1",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart2_layout(
                                                        dfs=initial_charts_data[
                                                            "chart-2-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-2",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart3_layout(
                                                        default_period=default_period,
                                                        dfs=initial_charts_data[
                                                            "chart-3-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-3",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                        ],
                                        className="mobile-chart-row g-0",
                                        align="stretch",
                                    ),
                                ],
                            ),
                            # Row 2 (Charts 4-6)
                            html.Div(
                                className="mobile-row-page",
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart4_layout(
                                                        default_period=default_period,
                                                        dfs=initial_charts_data[
                                                            "chart-4-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-4",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart5_layout(
                                                        default_period=CHART5_DEFAULT_TIMEFRAME,
                                                        dfs=initial_charts_data[
                                                            "chart-5-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-5",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    create_chart6_layout(
                                                        default_period=default_period,
                                                        dfs=initial_charts_data[
                                                            "chart-6-data-store"
                                                        ],
                                                        mobile=True,
                                                        chart_id="chart-6",
                                                    ),
                                                    body=True,
                                                    className="mobile-chart-card",
                                                ),
                                                width=4,
                                                className="mobile-chart-col",
                                            ),
                                        ],
                                        className="mobile-chart-row g-2",
                                        align="stretch",
                                    ),
                                ],
                            ),
                            # Placeholder for potential future updates or controls
                            html.Div(
                                id="mobile-dynamic-content", className="text-center"
                            ),
                            dcc.Interval(
                                id="mobile-interval",
                                interval=REFRESH_INTERVAL * 1000,
                                n_intervals=0,
                            ),
                        ],
                        fluid=True,
                    ),
                ],
            ),
        ],
    )
