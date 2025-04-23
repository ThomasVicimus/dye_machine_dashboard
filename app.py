import dash
from flask import Flask, redirect, request, jsonify
from flask_socketio import SocketIO
from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash_bootstrap_components as dbc
from user_agents import parse
import logging
import os
from datetime import datetime
import json
import pandas as pd
import plotly.graph_objects as go  # Keep go for placeholder figure
from apscheduler.schedulers.background import BackgroundScheduler

# Keep db import if needed for other parts, remove if only for chart 1
# from database_connection import db

# Import chart-specific functions and constants
from callbacks_chart_machine_usage import (
    load_initial_chart1_data,
    create_chart1_layout,
    create_period_buttons_chart1,
    register_chart1_callbacks,
    PERIOD_STORE_ID as CHART1_PERIOD_STORE_ID,  # Use alias to avoid potential future conflicts
)

# Configuration
ENABLE_TEMPLATES = False  # Set to False to use Dash-only mode

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_please_change")
socketio = SocketIO(server)

# Theme configuration
THEMES = {
    "dark_blue": {
        "background": "#1a1a2e",
        "text": "#ffffff",
        "card": "#16213e",
        "border": "#0f3460",
    },
    "black": {
        "background": "#000000",
        "text": "#ffffff",
        "card": "#1a1a1a",
        "border": "#333333",
    },
}

# Initialize Dash applications with theme support
desktop_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/dashboard/" if ENABLE_TEMPLATES else "/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/mobile/" if ENABLE_TEMPLATES else "/mobile/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

# --- Initial Data Load for Charts ---
# Load data specifically for chart 1 using the refactored function
(
    initial_chart1_figure,
    placeholder_chart_figure,
    chart1_available_periods,
    chart1_default_period,
) = load_initial_chart1_data()
# TODO: Load initial data for other charts here when they are added


# --- Desktop Layout Definition ---
desktop_app.layout = html.Div(
    id="main-container",
    children=[
        # Theme switcher (fixed position - Remains the same)
        html.Div(
            [
                dbc.Button(
                    "Dark Blue", id="theme-dark-blue", className="me-2", size="sm"
                ),
                dbc.Button("Black", id="theme-black", size="sm"),
            ],
            className="theme-switcher p-2",
            style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000},
        ),
        # Main content area
        html.Div(
            id="dashboard-content",
            children=[
                dbc.Container(
                    [
                        # Header Row (Remains the same)
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.H1(
                                        "Dye Machine Dashboard",
                                        id="dashboard-title",
                                        className="text-center my-3",
                                    ),
                                    width=12,
                                )
                            ]
                        ),
                        # Row for Period Buttons (Re-added)
                        dbc.Row(
                            [
                                dbc.Col(
                                    # Call the imported button creation function
                                    create_period_buttons_chart1(
                                        chart1_available_periods
                                    ),
                                    width=4,  # Align with first chart column
                                ),
                                dbc.Col(width=8),  # Empty columns to fill the row
                            ],
                            className="mb-2",
                        ),
                        # First row of charts
                        dbc.Row(
                            [
                                # Call the layout function (now just the graph column)
                                create_chart1_layout(initial_chart1_figure),
                                # Placeholder columns for other charts
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="chart-2",
                                            figure=placeholder_chart_figure,
                                        )
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="chart-3",
                                            figure=placeholder_chart_figure,
                                        )
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
                            ],
                            className="mb-2",
                            align="start",
                        ),
                        # Second row of charts
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="chart-4",
                                            figure=placeholder_chart_figure,
                                        )
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="chart-5",
                                            figure=placeholder_chart_figure,
                                        )
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
                                dbc.Col(
                                    [
                                        dcc.Graph(
                                            id="chart-6",
                                            figure=placeholder_chart_figure,
                                        )
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
                            ],
                            align="start",
                        ),
                    ],
                    fluid=True,
                    style={"padding": "20px"},
                )
            ],
        ),
        # Stores - Include stores needed by any chart callback
        dcc.Store(id="theme-store", data="dark_blue"),
        dcc.Store(id="screen-size-store"),
        dcc.Store(
            id=CHART1_PERIOD_STORE_ID, data=chart1_default_period
        ),  # Use the specific ID from the callbacks file
        dcc.Interval(
            id="interval-component", interval=60 * 1000, n_intervals=0
        ),  # Keep interval if needed
    ],
)

# --- Mobile Layout Definition (Unchanged) ---
mobile_app.layout = html.Div(
    [
        html.H2("Real-time Data - Mobile"),
        html.Div(id="mobile-content"),
        dcc.Interval(id="mobile-interval", interval=60 * 1000, n_intervals=0),
    ]
)

# --- Register Callbacks ---
register_chart1_callbacks(desktop_app)
# TODO: Register callbacks for other charts here when added

# --- Core App Callbacks (Theme, Screen Size, Mobile, Routing) ---


# Device detection and redirection (Simplified for Dash-only mode)
@server.route("/")
def index():
    # No need to check ENABLE_TEMPLATES as it's always False
    # No need for user agent parsing or template rendering
    return desktop_app.index()


# # Screen size detection endpoint (Unchanged)
# @server.route("/screen-size", methods=["POST"])
# def screen_size():
#     data = request.get_json()
#     width = data.get("width", 1920)
#     height = data.get("height", 1080)
#     logger.info(f"Screen size received via HTTP POST: {width}x{height}")
#     # Store or broadcast size via SocketIO if needed by callbacks
#     socketio.emit(
#         "screen_size_update", {"width": width, "height": height}, room=request.sid
#     )
#     return jsonify({"status": "success"})


# Theme switching callback (Unchanged)
@desktop_app.callback(
    Output("theme-store", "data"),
    [Input("theme-dark-blue", "n_clicks"), Input("theme-black", "n_clicks")],
)
def update_theme(dark_blue_clicks, black_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return "dark_blue"
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    theme = "dark_blue" if button_id == "theme-dark-blue" else "black"
    logger.info(f"Theme changed to: {theme}")
    return theme


# Theme application callback (Unchanged)
@desktop_app.callback(
    Output("dashboard-content", "style"),
    Input("theme-store", "data"),
)
def apply_theme(theme):
    theme_colors = THEMES[theme]
    content_style = {
        "backgroundColor": theme_colors["background"],
        "color": theme_colors["text"],
        "paddingTop": "60px",
    }
    return content_style


# Mobile callbacks (Unchanged)
@mobile_app.callback(
    Output("mobile-content", "children"), Input("mobile-interval", "n_intervals")
)
def update_mobile(n):
    # Example: Replace with actual mobile data logic
    return html.Div(
        [
            html.H4("Mobile Value: 42"),
            html.P(f"Update Time: {datetime.now().strftime('%H:%M:%S')}"),
        ]
    )


# SocketIO events (Unchanged)
@socketio.on("connect")
def handle_connect():
    logger.info(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


# SocketIO screen size handler (Store if needed by callbacks)
@socketio.on("screen_size")
def handle_screen_size(data):
    width = data.get("width")
    height = data.get("height")
    logger.info(
        f"Screen size received via SocketIO from {request.sid}: {width}x{height}"
    )
    # Example: Store size associated with session ID if needed
    # session_screen_sizes[request.sid] = {'width': width, 'height': height}
    # Optionally trigger updates via socketio.emit if Dash stores aren't used


# --- Scheduler and Server Start ---
scheduler = BackgroundScheduler()
# scheduler.add_job(...) # Add jobs if needed
scheduler.start()

if __name__ == "__main__":
    logger.info("Starting server...")
    socketio.run(server, host="0.0.0.0", port=8050, debug=True)
