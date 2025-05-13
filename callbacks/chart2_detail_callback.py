from dash import Input, Output, State, no_update
from dash import dcc
from dash import html
from dash import dash_table
import dash_bootstrap_components as dbc
from Database.serialize_df import deserialize_dataframe_dict
import logging

logger = logging.getLogger(__name__)


def register_chart2_detail_callback(app):

    @app.callback(
        Output(
            "mobile-page-content", "children"
        ),  # Replace content with the detail view
        Input("chart-2", "active_cell"),
        State("chart2-data-store", "data"),
        prevent_initial_call=True,
    )
    def load_table_on_click(active_cell, chart_data):
        if not active_cell:
            return no_update

        # Deserialize and get the desktop DataFrame
        deserialized = deserialize_dataframe_dict(chart_data)
        df_detail = deserialized.get("desktop", None)
        if df_detail is None:
            return html.Div("No detail data available.")

        # Build table
        detail_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df_detail.columns],
            data=df_detail.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"padding": "5px", "textAlign": "left", "color": "#ffffff"},
            style_header={"backgroundColor": "#2c3e50", "color": "white"},
        )

        # Create container with detail layout
        return html.Div(
            id="mobile-detail-wrapper-chart-2",
            style={
                "width": "100vw",
                "height": "100vh",
                "overflowY": "auto",
                "overflowX": "hidden",
                "position": "relative",
                "backgroundColor": "#000000",
                "zIndex": 1000,
            },
            children=[
                dbc.Container(
                    id="mobile-rotated-detail-content-chart-2",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Link(
                                        "Back",
                                        href="/",
                                        className="btn btn-secondary btn-sm",
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    html.H4(
                                        "Chart 2 Details",
                                        className="text-white text-center",
                                    ),
                                    width=True,
                                ),
                            ],
                            align="center",
                            className="mb-2",
                        ),
                        html.Div(detail_table),
                    ],
                    fluid=True,
                )
            ],
        )

    @app.callback(
        Output("chart-2", "page_current"),
        Input("chart-2-interval", "n_intervals"),
        State("chart-2", "page_current"),
        State("chart-2", "page_count"),
    )
    def turn_page(n, current, page_count):
        # advance one page, looping back at the end
        return (current + 1) % page_count
