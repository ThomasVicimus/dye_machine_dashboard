from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
import os
from datetime import datetime
from typing import Dict
import pandas as pd

from callbacks_chart_machine_usage import (
    load_initial_chart1_data,
    create_chart1_layout,
    create_period_buttons_chart1,
    register_chart1_callbacks,
    PERIOD_STORE_ID as CHART1_PERIOD_STORE_ID,  # Use alias to avoid potential future conflicts
)

# Assume ChartFactory is in chart_factory_MachineUasge.py
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data

# Assume db connection and data function are in database_connection.py
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
    suppress_callback_exceptions=True,  # Keep if callbacks will be added later
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

# --- Mobile Layout Definition (Rotated for Horizontal View) ---
mobile_app.layout = html.Div(
    id="mobile-wrapper",
    style={
        "width": "100vw",
        "height": "100vh",
        # "overflow": "hidden",  # Prevent scrollbars if rotation causes overflow
        "overflowY": "auto",
        "position": "relative",
        "backgroundColor": "#000000",  # Background moved to wrapper
    },
    children=[
        dbc.Container(
            id="mobile-rotated-content",  # Give the container an ID
            fluid=True,
            style={
                # Rotation and positioning CSS
                "transform": "rotate(90deg)",
                "transformOrigin": "top left",
                "width": "100vh",  # Takes viewport height as width
                "height": "100vw",  # Takes viewport width as height
                "position": "absolute",
                "top": "0",  # Position relative to the wrapper
                "left": "100%",
                "padding": "10px",  # Add some padding inside the rotated container
                # Add flex display to help rows stretch vertically if needed
                "display": "flex",
                "flexDirection": "column",
                "marginBottom": "5vh",
            },
            children=[
                dbc.Row(
                    dbc.Col(
                        html.H2(
                            "Mobile Dashboard",  # Simpler title now that orientation is implied
                            className="text-center pt-1 pb-0 text-white",  # Adjusted padding
                        ),
                        width=12,
                    )
                ),
                # Row 1 (Charts 1-3)
                dbc.Row(
                    [
                        create_chart1_layout(initial_chart1_figure, mobile=True),
                        # dbc.Col(
                        #     dcc.Graph(
                        #         id="mobile-chart-1",
                        #         figure=placeholder_chart_figure,
                        #         style={
                        #             "height": "20vh",
                        #             "width": "95%",
                        #         },  # Height adjusted
                        #     ),
                        #     width=4,  # Width changed
                        #     className="p-1",
                        # ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-2",
                                figure=placeholder_chart_figure,
                                style={
                                    "height": "20vh",
                                    "width": "95%",
                                },  # Height adjusted
                            ),
                            width=4,  # Width changed
                            className="p-0",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-3",
                                figure=placeholder_chart_figure,
                                style={
                                    "height": "20vh",
                                    "width": "95%",
                                },  # Height adjusted
                            ),
                            width=4,  # Width changed
                            className="p-0",
                        ),
                    ],
                    className="mb-1 g-0",
                    align="stretch",
                ),
                # Row 2 (Charts 4-6)
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-4",
                                figure=placeholder_chart_figure,
                                style={
                                    "height": "20vh",
                                    "width": "95%",
                                },  # Height adjusted
                            ),
                            width=4,  # Width changed
                            className="p-",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-5",
                                figure=placeholder_chart_figure,
                                style={
                                    "height": "20vh",
                                    "width": "95%",
                                },  # Height adjusted
                            ),
                            width=4,  # Width changed
                            className="p-0",
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="mobile-chart-6",
                                figure=placeholder_chart_figure,
                                style={
                                    "height": "20vh",
                                    "width": "95%",
                                },  # Height adjusted
                            ),
                            width=4,  # Width changed
                            className="p-0",
                        ),
                    ],
                    className="mb-1 g-0",
                    align="stretch",
                ),
                # Placeholder for potential future updates or controls
                html.Div(
                    id="mobile-dynamic-content", className="text-white text-center"
                ),  # Centered text
                dcc.Interval(
                    id="mobile-interval", interval=60 * 1000, n_intervals=0
                ),  # 60 seconds
            ],
        ),
        # --- Add Modal Component ---
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Machine Usage Details"),
                    close_button=True,
                    style={
                        "backgroundColor": "#000000",
                        "color": "white",
                        "borderBottom": "1px solid #333",
                    },  # Style header
                ),
                dbc.ModalBody(
                    id="mobile-modal-body",
                    style={
                        "maxHeight": "70vh",
                        "overflowY": "auto",
                        "backgroundColor": "#000000",
                        "color": "white",
                    },  # Style body
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="mobile-modal-close-button",
                        className="ms-auto",
                        n_clicks=0,
                    ),
                    style={
                        "backgroundColor": "#000000",
                        "color": "white",
                        "borderTop": "1px solid #333",
                    },  # Style footer
                ),
            ],
            id="mobile-details-modal",
            is_open=False,
            size="xl",  # Use a large size for the charts
            scrollable=False,  # Body handles scrolling
            centered=True,
            # style={
            #     "backgroundColor": "#000000",
            #     # "transform": "rotate(90deg)",
            #     # "transformOrigin": "top left",
            #     "width": "100vh",  # Takes viewport height as width
            #     "height": "100vw",  # Takes viewport width as height
            #     "position": "absolute",
            #     "top": "0",  # Position relative to the wrapper
            #     "left": "100%",
            # },  # Style modal, add rotation
            # className="modal-dark" # Alternative: Define a CSS class for dark theme
        ),
        # Add the period store used by chart 1 callbacks
        dcc.Store(
            id=CHART1_PERIOD_STORE_ID,
            storage_type="session",
            data=chart1_default_period,
        ),
    ],
)


# --- Basic Mobile Callback Example ---
@mobile_app.callback(
    Output("mobile-dynamic-content", "children"),
    Input("mobile-interval", "n_intervals"),
)
def update_mobile_content(n):
    # Replace with actual data fetching/update logic later
    return f"Last update: {datetime.now().strftime('%H:%M:%S')}"


# --- Add Callbacks for Modal ---
@mobile_app.callback(
    [
        Output("mobile-details-modal", "is_open"),
        Output("mobile-modal-body", "children"),
    ],
    [
        Input("mobile-chart-1", "clickData"),
        Input("mobile-modal-close-button", "n_clicks"),
    ],
    [State(CHART1_PERIOD_STORE_ID, "data"), State("mobile-details-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal(clickData, close_clicks, selected_period, is_open):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.PreventUpdate

    trigger = ctx.triggered[0]["prop_id"]
    if not clickData:
        # no click => nothing to do
        return dash.no_update, dash.no_update

    if trigger.startswith("mobile-chart-1.clickData") and clickData:
        try:
            # Fetch data for the selected period (similar to update_chart1_figure)
            conn_modal = db.connect()
            dfs_modal = get_MachineUsage_data(conn_modal)  # Fetch all data
            db.close(conn_modal)

            if selected_period not in dfs_modal:
                modal_content = html.Div(
                    f"Data not found for period: {selected_period}"
                )
                return True, modal_content

            # Instantiate factory and create detail charts
            # Assuming ChartFactory is defined and imported correctly
            chart_factory = MachineUsageChart({}, lang="zh_cn")
            detail_figures = chart_factory.create_machine_usage_chart_mobile_all_machine(
                selected_period,
                dfs_modal,
                # Adjust parameters if needed, e.g., smaller height/width for modal view
                plot_height=200,  # Smaller height for modal
                plot_width=220,  # Smaller width for modal
                title_font_size=12,
                subplot_title_font_size=10,
                legend_font_size=8,
                margin_top=30,
                margin_bottom=30,
                margin_left=5,
                margin_right=5,
            )

            # Create graph components for each figure
            modal_children = []
            if not detail_figures:
                modal_children = [
                    html.P("No detailed charts available for this period.")
                ]
            else:
                for i, fig in enumerate(detail_figures):
                    modal_children.append(
                        dcc.Graph(
                            id=f"modal-detail-chart-{i}",
                            figure=fig,
                            style={
                                "height": "230px"
                            },  # Give a fixed height to graphs inside scrollable body
                            config={"displayModeBar": False},
                        )
                    )

            return True, modal_children  # Open modal and set content

        except Exception as e:
            logger.error(
                f"Error loading modal details for period {selected_period}: {e}",
                exc_info=True,
            )
            modal_content = html.Div(f"Error loading details: {e}")
            if "conn_modal" in locals():
                db.close(conn_modal)
            return True, modal_content

    # 2) If Close button clicked → just close
    if trigger.startswith("mobile-modal-close-button.n_clicks") and is_open:
        return False, dash.no_update

    return dash.no_update, dash.no_update


# --- Server Start ---
if __name__ == "__main__":
    logger.info("Starting mobile server...")
    # Run on a different port
    mobile_app.run(
        host="0.0.0.0", port=8051, debug=True
    )  # Changed run to run_server for consistency
