from dash import Output, Input, State, no_update
import logging

logger = logging.getLogger(__name__)


def register_startup_modal_callbacks(app):
    """Register callbacks for initial modals to select period, timeframe, and theme."""

    # Handle period modal OK
    @app.callback(
        [
            Output("period-modal", "is_open"),
            Output("time-period-store", "data", allow_duplicate=True),
            Output("timeframe-modal", "is_open", allow_duplicate=True),
        ],
        Input("period-modal-ok", "n_clicks"),
        [State("period-modal", "is_open"), State("period-radio", "value")],
        prevent_initial_call=True,
    )
    def on_period_ok(n_clicks, is_open, selected_period):
        if n_clicks:
            logger.info(f"Period selected: {selected_period}")
            return False, selected_period, True  # Close period modal, open timeframe
        return is_open, no_update, no_update

    # Handle timeframe modal OK
    @app.callback(
        [
            Output("timeframe-modal", "is_open", allow_duplicate=True),
            Output("chart5-timeframe-store", "data", allow_duplicate=True),
            Output("theme-modal", "is_open", allow_duplicate=True),
        ],
        Input("timeframe-modal-ok", "n_clicks"),
        [State("timeframe-modal", "is_open"), State("timeframe-radio", "value")],
        prevent_initial_call=True,
    )
    def on_timeframe_ok(n_clicks, is_open, selected_timeframe):
        if n_clicks:
            logger.info(f"Chart5 timeframe selected: {selected_timeframe}")
            return False, selected_timeframe, True  # Close timeframe modal, open theme
        return is_open, no_update, no_update

    # Handle theme modal OK
    @app.callback(
        [
            Output("theme-modal", "is_open", allow_duplicate=True),
            Output("theme-store", "data", allow_duplicate=True),
        ],
        Input("theme-modal-ok", "n_clicks"),
        [State("theme-modal", "is_open"), State("theme-radio", "value")],
        prevent_initial_call=True,
    )
    def on_theme_ok(n_clicks, is_open, selected_theme):
        if n_clicks:
            logger.info(f"Theme selected: {selected_theme}")
            return False, selected_theme  # Close theme modal
        return is_open, no_update

    logger.info("Startup modal callbacks registered.")
