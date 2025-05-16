from dash import Input, Output, State, dcc, html, dash_table, callback_context as ctx
import dash_bootstrap_components as dbc
from Database.serialize_df import deserialize_dataframe_dict


def register_chart2_detail_callback(app):

    @app.callback(
        Output("mobile-page-content", "children"),
        [
            Input("mobile-url", "pathname"),  # Main router
            Input("chart-2", "active_cell"),  # Chart 2 cell click
        ],
        State("chart2-data-store", "data"),
        prevent_initial_call=True,
    )
    def handle_page_navigation(pathname, active_cell, chart_data):
        trigger = ctx.triggered_id

        # --- 1. Detail page via chart-2 cell click ---
        if trigger == "chart-2" and active_cell:
            deserialized = deserialize_dataframe_dict(chart_data)
            df_detail = deserialized.get("desktop", None)
            if df_detail is None:
                return html.Div("No detail data available.")

            detail_table = dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df_detail.columns],
                data=df_detail.to_dict("records"),
                style_table={"overflowX": "auto"},
                style_cell={"padding": "5px", "textAlign": "left", "color": "#ffffff"},
                style_header={"backgroundColor": "#2c3e50", "color": "white"},
            )

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

        # --- 2. Default or other routing logic ---
        if pathname == "/":
            return html.Div(
                "This is your dashboard homepage"
            )  # Or your dashboard layout
        elif pathname.startswith("/details/"):
            chart_id = pathname.split("/")[-1]
            return html.Div(f"Detail page for {chart_id}")
        else:
            return html.Div("404: Page not found")
