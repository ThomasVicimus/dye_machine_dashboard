from Database.database_connection import db
import logging
import dash_bootstrap_components as dbc
from dash import dcc, html
from ChartFactory.chartfactory_chart2 import create_chart2_figure
from function.dashboard_config import get_lane_count, get_chart2_page_interval

logger = logging.getLogger(__name__)


def create_chart2_layout(
    dfs: dict,
    chart_id: str = "chart-2",
    page_interval: int = None,
    desktop_row_count: int = None,
    mobile_row_count: int = None,
    mobile: bool = False,
    theme: str = "black",
):
    """Creates a DataTable showing machine status that auto-paginates.

    Args:
        dfs: Dictionary containing dataframes.
        chart_id: Unique ID for the table component.
        page_interval: Seconds between page turns (default from config).
        mobile: Whether the layout is for mobile view.
        theme: Current theme (black or dark_blue).
    """
    # Apply config defaults if not explicitly passed
    if page_interval is None:
        page_interval = get_chart2_page_interval()
    if desktop_row_count is None:
        desktop_row_count = get_lane_count("desktop")
    if mobile_row_count is None:
        mobile_row_count = get_lane_count("mobile")

    # Assuming df is in the dfs dictionary with a relevant key
    if mobile:
        mobile_option = "mobile"
    else:
        mobile_option = "desktop"
    df = dfs.get(mobile_option, None)
    df = df.get("all_machine", None)
    if df is None or df.empty:
        return html.Div("No data available", className="text-center p-4")

    # Define theme-based styling
    if theme == "black":
        header_bg_color = "#999999"
        text_color = "#fdfefe"
    else:  # dark_blue
        header_bg_color = "#16213e"
        text_color = "#fdfefe"

    fig = create_chart2_figure(
        df,
        mobile,
        desktop_row_count,
        mobile_row_count,
        text_color,
        header_bg_color,
    )

    # Desktop table
    if not mobile:
        table_component = html.Div(
            [
                dcc.Interval(
                    id=f"{chart_id}-interval",
                    interval=page_interval * 1000,  # Convert to milliseconds
                    n_intervals=0,
                ),
                html.Div(
                    fig,
                    className="chart2-table-wrap",
                    style={"flex": "1 1 auto", "minHeight": 0},
                ),
            ],
            className="chart2-card-wrap",
            style={
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "overflow": "hidden",
                "minHeight": 0,
            },
        )

        return table_component
    else:
        # Mobile table with adjusted sizing
        table_component = html.Div(
            [
                dcc.Interval(
                    id=f"{chart_id}-interval",
                    interval=page_interval * 1000,
                    n_intervals=0,
                ),
                html.Div(
                    fig,
                    className="chart2-table-wrap",
                    style={"flex": "1 1 auto", "minHeight": 0},
                ),
            ],
            className="chart2-card-wrap",
            style={
                "height": "100%",
                "display": "flex",
                "flexDirection": "column",
                "overflow": "hidden",
                "minHeight": 0,
            },
        )

        return table_component
