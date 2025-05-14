from Database.database_connection import db
import logging
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

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

    if df is None or df.empty:
        return dbc.Col(
            html.Div("No data available", className="text-center p-4"),
            width=4,
            className="p-2",
        )

    # Calculate total number of pages
    if not mobile:
        total_pages = (len(df) // desktop_row_count) + (
            1 if len(df) % desktop_row_count > 0 else 0
        )
    else:
        total_pages = (len(df) // mobile_row_count) + (
            1 if len(df) % mobile_row_count > 0 else 0
        )

    # Define theme-based styling
    if theme == "black":
        header_bg_color = "#999999"
        text_color = "#fdfefe"
    else:  # dark_blue
        header_bg_color = "#16213e"
        text_color = "#fdfefe"

    # Desktop table
    if not mobile:
        table_component = html.Div(
            [
                dcc.Interval(
                    id=f"{chart_id}-interval",
                    interval=page_interval * 1000,  # Convert to milliseconds
                    n_intervals=0,
                ),
                dash_table.DataTable(
                    id=chart_id,
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                    page_size=desktop_row_count,
                    page_current=0,
                    page_count=total_pages,
                    page_action="native",
                    style_table={
                        "overflowX": "auto",
                        "height": "100%",
                        "minHeight": "25vh",
                    },
                    style_cell={
                        "textAlign": "left",
                        "padding": "8px",
                        "color": text_color,
                    },
                    style_header={
                        "backgroundColor": header_bg_color,
                        "fontWeight": "bold",
                        "color": "#ffffff",
                    },
                ),
            ]
        )

        return dbc.Col(
            table_component,
            width=4,
            className="p-2",
        )
    else:
        # Mobile table with adjusted sizing
        table_component = html.Div(
            [
                dcc.Interval(
                    id=f"{chart_id}-interval",
                    interval=page_interval * 1000,
                    n_intervals=0,
                ),
                dash_table.DataTable(
                    id=chart_id,
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict("records"),
                    page_current=0,
                    page_size=mobile_row_count,
                    page_count=total_pages,
                    page_action="native",
                    style_table={
                        "overflowX": "auto",
                        "width": "100%",
                        "height": "100%",
                        # "tableLayout": "fixed",
                    },
                    # style_cell={
                    #     "minWidth": "10px",
                    #     "maxWidth": "20px",
                    #     "width": "50px",
                    #     "overflow": "hidden",
                    #     "textOverflow": "ellipsis",
                    #     "whiteSpace": "nowrap",
                    #     "color": text_color,
                    # },
                    style_cell={
                        "textAlign": "left",
                        "padding": "5px",
                        "fontSize": "12px",
                        "color": text_color,
                    },
                    style_header={
                        "backgroundColor": header_bg_color,
                        "fontWeight": "bold",
                        "color": "#ffffff",
                    },
                    # style_data_conditional=conditional_styling,
                ),
            ]
        )

        return dbc.Col(
            table_component,
            # dcc.Link(
            #     href=f"/details/{chart_id}",
            #     id=f"link-{chart_id}",
            #     style={
            #         "display": "block",
            #         "height": "100%",
            #         "width": "100%",
            #     },
            # ),
            width=4,
            className="p-0",
        )


# def register_callbacks(app):
#     """Register callbacks for the machine status table pagination.

#     This function should be called after app initialization to set up the
#     auto-pagination feature of the status table.

#     Args:
#         app: The Dash app instance.
#     """

#     def create_callback_for_table(chart_id):
#         @app.callback(
#             Output(chart_id, "page_current"),
#             [
#                 Input(f"{chart_id}-interval", "n_intervals"),
#                 Input(chart_id, "page_count"),
#             ],
#         )
#         def update_table_page(n_intervals, page_count):
#             """Auto-paginate the table based on interval ticks."""
#             if page_count <= 1:
#                 return 0
#             return n_intervals % page_count

#         return update_table_page
