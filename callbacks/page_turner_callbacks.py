import logging
import dash
from dash import Output, Input, State, callback_context
from Database.serialize_df import deserialize_dataframe_dict
import math
from function.dashboard_config import get_lane_count

logger = logging.getLogger(__name__)

def register_page_turner_callbacks(app, mobile=True):
    """Registers callbacks for the shared page turner buttons on the mobile main page."""

    # Keep the sticky control row on the main dashboard only (hide on /details/*).
    # This prevents the main-page controls from blocking buttons in the mobile detail overlay.
    _MAIN_CONTROLS_ROW_STYLE = {
        "position": "sticky",
        "top": "0",
        "zIndex": "1020",
        "backgroundColor": "#202020",
        "paddingTop": "5px",
        "paddingBottom": "5px",
    }

    @app.callback(
        Output("mobile-main-controls-row", "style"),
        Input("mobile-url", "pathname"),
    )
    def _toggle_main_controls_visibility(pathname):
        if pathname and pathname.startswith("/details/"):
            return {**_MAIN_CONTROLS_ROW_STYLE, "display": "none"}
        return _MAIN_CONTROLS_ROW_STYLE

    @app.callback(
        [
            Output("main-page-index-store", "data"),
            Output("main-page-indicator", "children"),
            Output("chart-2", "page_current"),
        ],
        [
            Input("main-prev-button", "n_clicks"),
            Input("main-next-button", "n_clicks"),
            Input("all-chart-data-store", "data"),
        ],
        [
            State("main-page-index-store", "data"),
            State("mobile-url", "pathname"),
        ],
        prevent_initial_call=True
    )
    def update_page_index(prev_clicks, next_clicks, all_chart_data, current_page, pathname):
        # Prevent updates when not on the main dashboard
        if pathname and pathname.startswith("/details/"):
            return dash.no_update, dash.no_update, dash.no_update

        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Calculate total pages from Chart 2 data
        chart2_data_serialized = all_chart_data.get("chart-2-data-store")
        total_pages = 1
        if chart2_data_serialized:
            try:
                chart2_data = deserialize_dataframe_dict(chart2_data_serialized)
                mobile_option = "mobile" if mobile else "desktop"
                df = chart2_data.get(mobile_option, {}).get("all_machine", None)
                if df is not None and not df.empty:
                    lane_count = get_lane_count("mobile" if mobile else "desktop")
                    total_pages = math.ceil(len(df) / lane_count)
            except Exception as e:
                logger.error(f"Error calculating total pages for page turner: {e}")

        new_page = current_page or 0

        # Handle button clicks
        if triggered_id == "main-prev-button":
            new_page = (new_page - 1) % total_pages
        elif triggered_id == "main-next-button":
            new_page = (new_page + 1) % total_pages
        # If all-chart-data-store updated, we might need to clamp new_page
        elif triggered_id == "all-chart-data-store":
            if new_page >= total_pages:
                new_page = 0

        indicator_text = f"{new_page + 1} / {total_pages}"
        
        return new_page, indicator_text, new_page
