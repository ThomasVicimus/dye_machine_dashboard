from dash import (
    Dash,
    html,
    dcc,
    Output,
    Input,
    State,
    callback_context,
    ALL,
    ClientsideFunction,
)
import dash
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
import os
from datetime import datetime

from callbacks_chart_machine_usage import (
    load_initial_chart1_data,
    create_chart1_layout,
    create_period_buttons_chart1,
    register_chart1_callbacks,
    PERIOD_STORE_ID as CHART1_PERIOD_STORE_ID,
)
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data
from database_connection import db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_mobile")

# Initialize Dash app for Mobile
mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/",  # Serve at root for this dedicated app
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
# * init charts
(
    initial_chart1_figure,
    placeholder_chart_figure,
    chart1_available_periods,
    chart1_default_period,
) = load_initial_chart1_data(mobile=True)


# --- Placeholder Figure ---
def create_placeholder_figure():
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "Chart Placeholder",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": "#888"},
            }
        ],
        paper_bgcolor="#1a1a1a",  # Example background, adjust as needed
        plot_bgcolor="#1a1a1a",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


placeholder_chart_figure = create_placeholder_figure()


# --- Mobile Layout Definition ---
mobile_app.layout = html.Div(
    id="mobile-wrapper",
    style={
        "width": "100vw",
        "height": "100vh",
        "overflowY": "auto",
        "position": "relative",
        "backgroundColor": "#000000",
    },
    children=[
        dcc.Store(id=CHART1_PERIOD_STORE_ID, data=chart1_default_period),
        dbc.Container(
            id="mobile-rotated-content",
            children=[
                dbc.Row(
                    dbc.Col(
                        html.H2(
                            "Mobile Dashboard",
                            className="text-center pt-1 pb-0 text-white",
                        ),
                        width=12,
                    )
                ),
                dbc.Row(
                    [
                        create_chart1_layout(initial_chart1_figure, mobile=True),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-2",
                                figure=placeholder_chart_figure,
                                style={"height": "20vh", "width": "95%"},
                            ),
                            width=4,
                            className="p-0",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-3",
                                figure=placeholder_chart_figure,
                                style={"height": "20vh", "width": "95%"},
                            ),
                            width=4,
                            className="p-0",
                        ),
                    ],
                    className="mb-1 g-0",
                    align="stretch",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-4",
                                figure=placeholder_chart_figure,
                                style={"height": "20vh", "width": "95%"},
                            ),
                            width=4,
                            className="p-0",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-5",
                                figure=placeholder_chart_figure,
                                style={"height": "20vh", "width": "95%"},
                            ),
                            width=4,
                            className="p-0",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-6",
                                figure=placeholder_chart_figure,
                                style={"height": "20vh", "width": "95%"},
                            ),
                            width=4,
                            className="p-0",
                        ),
                    ],
                    className="mb-1 g-0",
                    align="stretch",
                ),
                html.Div(
                    id="mobile-dynamic-content", className="text-white text-center"
                ),
                dcc.Interval(id="mobile-interval", interval=60 * 1000, n_intervals=0),
            ],
            fluid=True,
            style={
                "transform": "rotate(90deg)",
                "transformOrigin": "top left",
                "width": "100vh",
                "height": "100vw",
                "position": "absolute",
                "top": "0",
                "left": "100%",
                "padding": "10px",
                "display": "flex",
                "flexDirection": "column",
                "marginBottom": "5vh",
            },
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Machine Details"), close_button=True),
                dbc.ModalBody(
                    html.Div(
                        id="swiper-modal-content",
                        className="swiper-container-popup",
                        style={
                            "transform": "rotate(90deg)",
                            "transformOrigin": "center center",
                            "width": "calc(100vh - 100px)",
                            "height": "calc(100vw - 100px)",
                            "overflow": "hidden",
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                            "padding": "0",
                            "margin": "auto",
                        },
                    )
                ),
            ],
            id="swiper-modal",
            is_open=False,
            size="xl",
            centered=True,
            scrollable=True,
            dialog_style={"maxWidth": "95vw", "height": "90vh"},
        ),
    ],
)

mobile_app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="initializeSwiper"),
    Output("swiper-modal", "id"),
    Input("swiper-modal-content", "children"),
    prevent_initial_call=True,
)


@mobile_app.callback(
    Output("mobile-dynamic-content", "children"),
    Input("mobile-interval", "n_intervals"),
)
def update_mobile_content(n):
    return f"Last update: {datetime.now().strftime('%H:%M:%S')}"


@mobile_app.callback(
    Output("swiper-modal-content", "children"),
    Output("swiper-modal", "is_open"),
    Input("mobile-chart-1-graph", "clickData"),
    State(CHART1_PERIOD_STORE_ID, "data"),
    State("swiper-modal", "is_open"),
    prevent_initial_call=True,
)
def display_swiper_charts(clickData, selected_period, is_open):
    triggered_id = callback_context.triggered_id
    if (
        triggered_id == "mobile-chart-1-graph"
        and clickData
        and selected_period
        and selected_period not in ["No Data", "Error"]
    ):
        logger.info(f"Chart 1 clicked. Opening modal for period: {selected_period}")

        try:
            conn = db.connect()
            dfs_all_machines = get_MachineUsage_data(conn)
            db.close(conn)

            if selected_period not in dfs_all_machines:
                logger.warning(
                    f"Period '{selected_period}' not found in data for modal."
                )
                return html.Div("Data for selected period not found."), True

            chart_factory = MachineUsageChart({}, lang="zh_cn")
            figures = chart_factory.create_machine_usage_chart_mobile_all_machine(
                period=selected_period,
                dfs=dfs_all_machines,
                plot_height=350,
                plot_width=450,
                title_font_size=12,
                subplot_title_font_size=10,
                legend_font_size=8,
                margin_top=40,
                margin_bottom=40,
            )

            if not figures:
                logger.warning(
                    f"No figures generated by factory for period {selected_period}"
                )
                return html.Div("Could not generate detailed charts."), True

            slides = []
            for i, fig in enumerate(figures):
                slide = html.Div(
                    className="swiper-slide",
                    children=[
                        dcc.Graph(
                            id={"type": "modal-chart", "index": i},
                            figure=fig,
                            style={"height": "100%", "width": "100%"},
                            config={"displayModeBar": False},
                        )
                    ],
                    style={"textAlign": "center"},
                )
                slides.append(slide)

            swiper_layout = html.Div(
                className="swiper",
                children=[
                    html.Div(className="swiper-wrapper", children=slides),
                    html.Div(className="swiper-pagination"),
                    html.Div(className="swiper-button-prev"),
                    html.Div(className="swiper-button-next"),
                ],
                style={"height": "50vh"},
            )

            return swiper_layout, True

        except Exception as e:
            logger.error(f"Error generating swiper charts: {e}", exc_info=True)
            if "conn" in locals() and conn:
                db.close(conn)
            return dbc.Alert(f"Error loading details: {e}", color="danger"), True

    return dash.no_update, is_open


# Register Chart 1's original callbacks (period selection, main chart update)
# Make sure this uses the correct 'mobile_app' instance
# NOTE: This assumes register_chart1_callbacks is compatible with the mobile layout's structure
#       (e.g., uses CHART1_PERIOD_STORE_ID, mobile-chart-1-graph if needed, etc.)
#       You might need to adjust register_chart1_callbacks if it wasn't designed
#       to work independently or expects different component IDs/structure.
#       For now, let's assume it works or needs minor tweaks inside that function if issues arise.
# *****************************************************************************
# * IMPORTANT: Review `register_chart1_callbacks` in `callbacks_chart_machine_usage.py` *
# * to ensure it correctly updates the `mobile-chart-1-graph` figure        *
# * and uses `CHART1_PERIOD_STORE_ID` correctly in this mobile context.     *
# *****************************************************************************
# register_chart1_callbacks(mobile_app) # TODO: Uncomment and verify this works correctly

# --- Server Start ---
if __name__ == "__main__":
    logger.info("Starting mobile server...")
    mobile_app.run(host="0.0.0.0", port=8051, debug=True)
