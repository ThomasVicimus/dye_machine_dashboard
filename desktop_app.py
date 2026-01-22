import dash
from flask import Flask, redirect, request, render_template, jsonify
from flask_socketio import SocketIO
from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash_bootstrap_components as dbc
from user_agents import parse
import logging
import os
import socket
from callbacks.select_time_period_callback import (
    register_time_period_callbacks,
    register_chart5_timeframe_callbacks,
    register_txt_cards_callbacks,
    register_auto_refresh_callbacks,
    register_chart2_data_refresh_callback,
)

# from callbacks.detail_page_callbacks import register_mobile_page_callbacks
from callbacks.select_theme_callback import register_theme_callbacks

from callbacks.refresher_callback import (
    register_chart2_page_turner,
)
from Database.fetch_all_charts_data import *
from layouts.desktop_dashboard_layout import create_desktop_layout
from callbacks.startup_modal_callbacks import register_startup_modal_callbacks
from function.dashboard_config import get_default_theme, get_default_lang

db = DatabaseConnection()
conn = db.connect()
# * Get data for all charts
data = get_all_charts_data(db)

# Initialize Flask
server = Flask(__name__)
server.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_key_please_change")
socketio = SocketIO(server)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get defaults from config
DEFAULT_THEME = get_default_theme()
DEFAULT_LANG = get_default_lang()

def _get_lan_ip() -> str:
    """
    Best-effort LAN IP detection for printing a usable URL on the local network.
    This does not require external connectivity; it just uses routing to pick an interface.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return "127.0.0.1"

desktop_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

desktop_app.layout = create_desktop_layout(
    initial_charts_data=data,
    color_theme=DEFAULT_THEME,
    lang=DEFAULT_LANG,
    default_period="今天",
)

# Chart 1, 3, 4, 6
register_time_period_callbacks(
    app=desktop_app,
    # chart_id="chart-1",
    mobile=False,
    lang=DEFAULT_LANG,
)

# Chart 5
register_chart5_timeframe_callbacks(
    app=desktop_app,
    mobile=False,
    lang=DEFAULT_LANG,
)

# Chart 2
register_theme_callbacks(
    app=desktop_app,
    default_color=DEFAULT_THEME,
    default_lang=DEFAULT_LANG,
)

# Chart 2
register_chart2_page_turner(desktop_app)

# Chart 3, 6
register_txt_cards_callbacks(
    app=desktop_app,
    mobile=False,
    lang=DEFAULT_LANG,
)

# All Charts
register_auto_refresh_callbacks(
    app=desktop_app,
    mobile=False,
    lang="zh_cn",
)

# Chart 2
register_chart2_data_refresh_callback(
    app=desktop_app,
    mobile=False,
    lang="zh_cn",
)

# Register startup modals (must be after stores are included in layout)
register_startup_modal_callbacks(desktop_app)

# register_mobile_page_callbacks(
#     app=desktop_app,
#     chart_id="chart-1",
#     default_period="今天",
#     lang="zh_cn",
# )
if __name__ == "__main__":
    host = os.environ.get("DASH_HOST", "0.0.0.0")
    port = int(os.environ.get("DASH_PORT", "8051"))
    lan_ip = _get_lan_ip()
    logger.info("Starting desktop server...")
    logger.info(f"Local URL: http://127.0.0.1:{port}/")
    logger.info(f"LAN URL:   http://{lan_ip}:{port}/")
    desktop_app.run(
        host=host,
        port=port,
    )
    # debug=True,
