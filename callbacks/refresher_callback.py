from dash import Input, Output, State


def register_chart2_page_turner(app):
    """Register callbacks for the machine status table pagination.

    This function should be called after app initialization to set up the
    auto-pagination feature of the status table.

    Args:
        app: The Dash app instance.
    """

    @app.callback(
        Output("chart-2", "page_current"),
        Input("chart-2-interval", "n_intervals"),
        State("chart-2", "page_current"),
        State("chart-2", "page_count"),
    )
    def turn_page(n, current, page_count):
        # advance one page, looping back at the end
        return (current + 1) % page_count
