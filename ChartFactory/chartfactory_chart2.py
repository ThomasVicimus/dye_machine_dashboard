# import dash_bootstrap_components as dbc
from dash import dash_table


def create_chart2_figure(
    df,
    mobile,
    mobile_row_count,
    desktop_row_count,
    total_pages,
    text_color,
    header_bg_color,
):
    chart_id = "chart-2"
    if not mobile:
        fig = dash_table.DataTable(
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
                # "tableLayout": "fixed",
            },
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
        )
    return fig
