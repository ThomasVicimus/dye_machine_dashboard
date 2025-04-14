from flask import Flask, redirect, request, render_template, jsonify
from flask_socketio import SocketIO
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from user_agents import parse
import logging
import os
from datetime import datetime
import json
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

# Configuration
ENABLE_TEMPLATES = True  # Set to False to use Dash-only mode

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
)

mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/mobile/" if ENABLE_TEMPLATES else "/mobile/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

# Template-based dashboard layout
desktop_app.layout = html.Div(
    [
        # Theme switcher
        html.Div(
            [
                dbc.Button("Dark Blue", id="theme-dark-blue", className="me-2"),
                dbc.Button("Black", id="theme-black"),
            ],
            className="theme-switcher",
        ),
        # Main content
        html.Div(
            [
                html.H1("Real-time Data Dashboard - Desktop", id="dashboard-title"),
                dcc.Graph(id="live-graph"),
                dbc.Table(id="data-table", striped=True, bordered=True, hover=True),
                dcc.Interval(
                    id="interval-component", interval=60 * 1000, n_intervals=0
                ),
            ],
            id="dashboard-content",
        ),
        # Store for theme and screen size
        dcc.Store(id="theme-store", data="dark_blue"),
        dcc.Store(id="screen-size-store"),
    ]
)

# Mobile dashboard layout
mobile_app.layout = html.Div(
    [
        html.H2("Real-time Data - Mobile"),
        html.Div(id="mobile-content"),
        dcc.Interval(id="mobile-interval", interval=60 * 1000, n_intervals=0),
    ]
)


# Device detection and redirection with screen size detection
@server.route("/")
def index():
    if not ENABLE_TEMPLATES:
        return redirect("/dashboard/")

    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)

    if user_agent.is_mobile:
        return render_template("mobile.html")
    else:
        return render_template("desktop.html")


# Screen size detection endpoint
@server.route("/screen-size", methods=["POST"])
def screen_size():
    data = request.get_json()
    screen_width = data.get("width", 1920)
    screen_height = data.get("height", 1080)

    # Store screen size in session or database for later use
    # This can be used to adjust font sizes and layouts
    logger.info(f"Screen size detected: {screen_width}x{screen_height}")

    return jsonify({"status": "success"})


# Theme switching callback
@desktop_app.callback(
    Output("theme-store", "data"),
    [Input("theme-dark-blue", "n_clicks"), Input("theme-black", "n_clicks")],
)
def update_theme(dark_blue_clicks, black_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "dark_blue"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return "dark_blue" if button_id == "theme-dark-blue" else "black"


# Theme application callback
@desktop_app.callback(
    [Output("dashboard-content", "style"), Output("dashboard-title", "style")],
    Input("theme-store", "data"),
)
def apply_theme(theme):
    theme_colors = THEMES[theme]
    content_style = {
        "backgroundColor": theme_colors["background"],
        "color": theme_colors["text"],
        "padding": "20px",
        "borderRadius": "10px",
        "border": f'1px solid {theme_colors["border"]}',
    }
    title_style = {
        "color": theme_colors["text"],
        "textAlign": "center",
        "marginBottom": "20px",
    }
    return content_style, title_style


# Desktop callbacks
@desktop_app.callback(
    [Output("live-graph", "figure"), Output("data-table", "children")],
    Input("interval-component", "n_intervals"),
)
def update_desktop(n):
    # This will be replaced with actual data from database_connection.py
    mock_data = {"value": [10, 20, 30, 40, 50], "time": [1, 2, 3, 4, 5]}
    df = pd.DataFrame(mock_data)

    # Create graph
    figure = {
        "data": [{"x": df["time"], "y": df["value"], "type": "line"}],
        "layout": {
            "title": f'Update Time: {datetime.now().strftime("%H:%M:%S")}',
            "paper_bgcolor": THEMES["dark_blue"]["background"],
            "plot_bgcolor": THEMES["dark_blue"]["card"],
            "font": {"color": THEMES["dark_blue"]["text"]},
        },
    }

    # Create table
    table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    return figure, table


# Mobile callbacks
@mobile_app.callback(
    Output("mobile-content", "children"), Input("mobile-interval", "n_intervals")
)
def update_mobile(n):
    # This will be replaced with actual data from database_connection.py
    mock_data = {"value": [42]}
    df = pd.DataFrame(mock_data)

    return html.Div(
        [
            html.H4(f"Current Value: {df['value'].iloc[0]}"),
            html.P(f"Update Time: {datetime.now().strftime('%H:%M:%S')}"),
        ]
    )


# SocketIO events
@socketio.on("connect")
def handle_connect():
    logger.info("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")


@socketio.on("screen_size")
def handle_screen_size(data):
    logger.info(f"Screen size received via SocketIO: {data}")
    # Store screen size information for this client


# Initialize scheduler
scheduler = BackgroundScheduler()
# scheduler.add_job(func=get_data, trigger="interval", seconds=60)
scheduler.start()

if __name__ == "__main__":
    logger.info("Starting server...")
    logger.info(f"Template mode: {'Enabled' if ENABLE_TEMPLATES else 'Disabled'}")
    socketio.run(server, host="0.0.0.0", port=8050, debug=True)
