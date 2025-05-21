from Database.database_connection import db
import logging
import dash_bootstrap_components as dbc
from dash import dcc, html
from ChartFactory.chartfactory_chart2 import create_chart2_figure

logger = logging.getLogger(__name__)


def create_chart2_layout(
    dfs: dict,
    chart_id: str = "chart-2",
    page_interval: int = 15,
    desktop_row_count: int = 6,
    mobile_row_count: int = 4,
    mobile: bool = False,
    theme: str = "black",
):
    """Creates a DataTable showing machine status that auto-paginates.

    Args:
        dfs: Dictionary containing dataframes.
        chart_id: Unique ID for the table component.
        page_interval: Seconds between page turns (default: 15).
        mobile: Whether the layout is for mobile view.
        theme: Current theme (black or dark_blue).
    """
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
                fig,
            ],
            style={"height": "100%", "overflowY": "auto"},
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
                fig,
            ],
            style={"height": "100%", "overflowY": "auto"},
        )

        return table_component
