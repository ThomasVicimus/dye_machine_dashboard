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
        """Advance to the next page unless this is the initial interval tick (n == 0).

        Dash's Interval component starts at n_intervals == 0 and then increments.
        Without this guard, the very first callback execution immediately
        increments the page, so the table appears to start on page 2.  We
        keep the current page when n == 0 and only advance from the second
        tick onward.
        """

        # Safety defaults
        if page_count in (None, 0):
            page_count = 1

        if n is None or n == 0:
            # Stay on whatever page Dash initialised with (usually 0)
            return current

        # advance one page, looping back at the end
        return ((current or 0) + 1) % page_count
