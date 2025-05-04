import dash
from flask import Flask, redirect, request, render_template, jsonify
from flask_socketio import SocketIO
from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash_bootstrap_components as dbc
from user_agents import parse
import logging
import os
from callbacks.select_time_period_callback import register_time_period_callbacks
from callbacks.detail_page_callbacks import register_mobile_page_callbacks
from callbacks.select_theme_callback import register_theme_callbacks
from Database.fetch_all_charts_data import *
from layouts.desktop_dashboard_layout import create_desktop_layout

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

mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

mobile_app.layout = create_desktop_layout(
    initial_charts_data=data,
    color_theme="black",
    lang="zh_cn",
    default_period="今日",
)


register_time_period_callbacks(
    app=mobile_app,
    chart_id="chart-1",
    mobile=False,
    lang="zh_cn",
)
register_theme_callbacks(
    app=mobile_app,
    default_color="black",
    default_lang="zh_cn",
)

# register_mobile_page_callbacks(
#     app=mobile_app,
#     chart_id="chart-1",
#     default_period="今日",
#     lang="zh_cn",
# )
if __name__ == "__main__":
    logger.info("Starting mobile server...")
    mobile_app.run(host="0.0.0.0", port=8051, debug=True)
