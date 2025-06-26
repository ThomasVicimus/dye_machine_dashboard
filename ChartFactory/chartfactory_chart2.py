# import dash_bootstrap_components as dbc
from dash import dash_table
import logging

logger = logging.getLogger(__name__)


def create_chart2_figure(
    df,
    mobile,
    # desktop_row_count: int = 4,
    desktop_row_count: int = 6,
    mobile_row_count: int = 4,
    header_bg_color="#2774a7",
    text_color="#fdfefe",
):
    chart_id = "chart-2"

    # Calculate total number of pages
    if not mobile:
        total_pages = (len(df) // desktop_row_count) + (
            1 if len(df) % desktop_row_count > 0 else 0
        )
    else:
        total_pages = (len(df) // mobile_row_count) + (
            1 if len(df) % mobile_row_count > 0 else 0
        )

    if not mobile:
        fig = dash_table.DataTable(
            id=chart_id,
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_size=desktop_row_count,
            page_current=0,
            page_count=total_pages,
            page_action="native",
            css=[
                {
                    "selector": ".previous-next-container",
                    "rule": "display: none !important;",
                }
            ],
            style_table={
                "overflowX": "auto",
                "height": "100%",
                "minHeight": "25vh",
            },
            style_cell={
                "textAlign": "center",
                "padding": "6px",
                "color": text_color,
                "fontFamily": "Microsoft YaHei",
                "width": "auto",
                "minWidth": "80px",
                "whiteSpace": "normal",
            },
            style_header={
                "backgroundColor": header_bg_color,
                "fontWeight": "normal",
                "color": "#ffffff",
                "fontFamily": "Microsoft YaHei",
                "textAlign": "center",
                "width": "auto",
                "minWidth": "80px",
            },
            css=[
                {
                    "selector": ".previous-next-container",
                    "rule": "display: none;",
                }
            ],
        )
    else:
        fig = dash_table.DataTable(
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
                # "minHeight": "20vh",
                # "tableLayout": "fixed",
            },
            style_cell={
                "textAlign": "center",
                "padding": "4px",
                "fontSize": "10px",
                "color": text_color,
                "fontFamily": "Microsoft YaHei",
                "width": "auto",
                "minWidth": "60px",
                "whiteSpace": "normal",
            },
            style_header={
                "backgroundColor": header_bg_color,
                "fontSize": "9px",
                "fontWeight": "normal",
                "color": "#ffffff",
                "fontFamily": "Microsoft YaHei",
                "textAlign": "center",
                "width": "auto",
                "minWidth": "60px",
            },
        )
    return fig


def create_chart2_figure_detail(df):
    header_bg_color = "#2774a7"
    text_color = "#fdfefe"
    chart_id = "mobile-detail-chart-chart-2-0"

    fig = dash_table.DataTable(
        id=chart_id,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        page_action="none",
        style_table={
            "overflowX": "auto",
            "height": "100%",
            "minHeight": "25vh",
        },
        style_cell={
            "textAlign": "center",
            "padding": "8px",
            "color": text_color,
            "fontFamily": "Microsoft YaHei",
            "width": "auto",
            "minWidth": "100px",
            "whiteSpace": "normal",
        },
        style_header={
            "backgroundColor": header_bg_color,
            "fontWeight": "normal",
            "color": "#ffffff",
            "fontFamily": "Microsoft YaHei",
            "textAlign": "center",
            "width": "auto",
            "minWidth": "100px",
        },
    )
    return fig
