from flask import Flask, redirect, request, render_template, jsonify
from flask_socketio import SocketIO
from dash import Dash, html, dcc, Output, Input, State, callback_context, ALL
import dash
import dash_bootstrap_components as dbc
from user_agents import parse
import logging
import os
from datetime import datetime
import json
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from database_connection import db
import plotly.graph_objects as go

# Import the chart factory
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data

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
    suppress_callback_exceptions=True,  # Allow callbacks on elements not present in initial layout
)

mobile_app = Dash(
    __name__,
    server=server,
    url_base_pathname="/mobile/" if ENABLE_TEMPLATES else "/mobile/",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

# --- Data Fetching and Initial Chart Setup ---
try:
    conn = db.connect()
    # Assume get_MachineUsage_data returns dict: {period: {"avg": df, "best": df, "worst": df}}
    dfs_chart1 = get_MachineUsage_data(db)
    available_periods = list(dfs_chart1.keys())
    if not available_periods:
        logger.warning("No periods found in dfs_chart1 data.")
        default_period = "No Data"
        initial_chart1_figure = go.Figure().update_layout(
            title="No Data Available"
        )  # Placeholder figure
    else:
        default_period = available_periods[0]
        logger.info(f"Available periods: {available_periods}")
        logger.info(f"Default period: {default_period}")

        # Create chart factory instance
        # Note: The factory itself doesn't need the period-specific data if we pass it during chart creation
        chart_factory = MachineUsageChart(
            {}, lang="zh_cn"
        )  # Pass empty dict or handle differently if needed

        # Create the initial figure for the first chart
        initial_data = dfs_chart1
        initial_chart1_figure = chart_factory.create_machine_usage_chart(
            default_period,
            initial_data,
            # TODO: Add dynamic sizing parameters here based on screen size/theme
        )

        # Create a generic chart for other slots (using sample data or first period)
        # This prevents needing to fetch/calculate data for all 6 slots initially
        placeholder_chart_figure = (
            initial_chart1_figure  # Use the same figure for placeholders
        )

except Exception as e:
    logger.error(
        f"Error during initial data fetching or chart creation: {e}", exc_info=True
    )
    available_periods = []
    default_period = "Error"
    initial_chart1_figure = go.Figure().update_layout(title="Error Loading Chart 1")
    placeholder_chart_figure = go.Figure().update_layout(title="Error Loading Chart")
finally:
    if "conn" in locals() and conn:
        db.close(conn)


# --- Desktop Layout Definition ---
def create_period_buttons(periods):
    if not periods:
        return dbc.Alert("No periods available", color="warning")
    return dbc.ButtonGroup(
        [
            dbc.Button(
                period,
                id={"type": "period-button", "index": period},
                color="primary",
                outline=True,
                size="sm",
            )
            for period in periods
        ],
        className="mb-2",
    )


desktop_app.layout = html.Div(
    id="main-container",
    children=[
        # Theme switcher (fixed position)
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
                        # First row of charts
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            id="period-button-container",
                                            children=create_period_buttons(
                                                available_periods
                                            ),
                                        ),
                                        dcc.Graph(
                                            id="chart-1", figure=initial_chart1_figure
                                        ),
                                    ],
                                    width=4,
                                    className="p-2",
                                ),
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
                            ]
                        ),
                    ],
                    fluid=True,
                    style={"max-width": "1920px", "padding": "20px"},  # Keep max-width
                )
            ],
        ),
        # Stores
        dcc.Store(id="theme-store", data="dark_blue"),
        dcc.Store(id="screen-size-store"),
        dcc.Store(id="selected-period-store", data=default_period),
        dcc.Interval(
            id="interval-component", interval=60 * 1000, n_intervals=0
        ),  # Keep interval if needed
    ],
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
        # Pass initial theme to template if needed
        return render_template("desktop.html", initial_theme="dark_blue")


# Screen size detection endpoint
@server.route("/screen-size", methods=["POST"])
def screen_size():
    data = request.get_json()
    width = data.get("width", 1920)
    height = data.get("height", 1080)
    logger.info(f"Screen size received via HTTP POST: {width}x{height}")
    # Optionally, broadcast this info via SocketIO to update the specific client's Dash app
    # Or store it in a session associated with the request/client
    socketio.emit(
        "screen_size_update", {"width": width, "height": height}, room=request.sid
    )
    return jsonify({"status": "success"})


# Theme switching callback
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


# Theme application callback
@desktop_app.callback(
    Output("dashboard-content", "style"),
    Input("theme-store", "data"),
)
def apply_theme(theme):
    theme_colors = THEMES[theme]
    content_style = {
        "backgroundColor": theme_colors["background"],
        "color": theme_colors["text"],
        "paddingTop": "60px",  # Add padding to avoid overlap with fixed theme switcher
        # Other styles like padding, border can be applied here if needed
        # "padding": "20px",
        # "borderRadius": "10px",
        # "border": f'1px solid {theme_colors["border"]}',
    }
    return content_style


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
    logger.info(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on("screen_size")
def handle_screen_size(data):
    width = data.get("width")
    height = data.get("height")
    logger.info(
        f"Screen size received via SocketIO from {request.sid}: {width}x{height}"
    )
    # Store screen size information associated with this client (e.g., in a dictionary)
    # Example: session_screen_sizes[request.sid] = {'width': width, 'height': height}
    # Trigger a callback to update the charts for this specific client if needed
    # This requires modifying the chart callback to take screen size as input


# Callback to update the selected period store when a button is clicked
@desktop_app.callback(
    Output("selected-period-store", "data"),
    Input({"type": "period-button", "index": ALL}, "n_clicks"),
    State("selected-period-store", "data"),
    prevent_initial_call=True,
)
def update_selected_period(n_clicks_list, current_period):
    ctx = callback_context
    if not ctx.triggered:
        return current_period  # No button clicked, return current state

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if not button_id:  # Should not happen with pattern matching
        return current_period

    # The button_id is a JSON string like '{"index":"PeriodA","type":"period-button"}'
    try:
        button_info = json.loads(button_id)
        selected_period = button_info.get("index")
        if selected_period:
            logger.info(f"Period button clicked: {selected_period}")
            return selected_period
    except json.JSONDecodeError:
        logger.error(f"Failed to parse button ID: {button_id}")
        return current_period

    return current_period  # Return current if parsing failed


# Callback to update chart-1 based on the selected period
@desktop_app.callback(
    Output("chart-1", "figure"),
    Input("selected-period-store", "data"),
    # TODO: Add Input for screen size from dcc.Store(id="screen-size-store")
    # TODO: Add Input for theme from dcc.Store(id="theme-store")
    prevent_initial_call=True,  # IMPORTANT: Initial figure is set in the layout
)
def update_chart1_figure(selected_period):
    logger.info(f"Updating chart-1 for period: {selected_period}")
    if (
        not selected_period
        or selected_period == "No Data"
        or selected_period == "Error"
    ):
        return go.Figure().update_layout(title=f"Invalid Period: {selected_period}")

    try:
        # Re-fetch data or use cached data if available and appropriate
        # For simplicity, re-fetching here. Consider caching for performance.
        conn_update = db.connect()
        dfs_update = get_MachineUsage_data(conn_update)
        db.close(conn_update)

        if selected_period not in dfs_update:
            logger.warning(
                f"Selected period '{selected_period}' not found in updated data."
            )
            return go.Figure().update_layout(
                title=f"Data not found for {selected_period}"
            )

        # period_data = dfs_update[selected_period]
        # Recreate the factory - could be optimized by creating once
        chart_factory_update = MachineUsageChart({}, lang="zh_cn")

        # TODO: Get screen size and theme from Inputs added above
        # screen_width = ...
        # theme = ...
        # Calculate plot size/font based on screen_width and theme
        # plot_height, plot_width, title_font_size, ... = calculate_sizes(screen_width, theme)

        new_figure = chart_factory_update.create_machine_usage_chart(
            selected_period,
            dfs_update,
            # Pass calculated sizes here
            # plot_height=plot_height,
            # plot_width=plot_width,
            # ...
        )
        return new_figure

    except Exception as e:
        logger.error(
            f"Error updating chart-1 for period {selected_period}: {e}", exc_info=True
        )
        return go.Figure().update_layout(
            title=f"Error loading data for {selected_period}"
        )


# Initialize scheduler
scheduler = BackgroundScheduler()
# scheduler.add_job(func=get_data, trigger="interval", seconds=60)
scheduler.start()

if __name__ == "__main__":
    logger.info("Starting server...")
    logger.info(f"Template mode: {'Enabled' if ENABLE_TEMPLATES else 'Disabled'}")
    # Use host='0.0.0.0' to make accessible on the network
    socketio.run(server, host="0.0.0.0", port=8050, debug=True)
