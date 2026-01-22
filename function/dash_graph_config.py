"""
Shared Dash `dcc.Graph` configuration.

This project is primarily mobile-first; we default to non-interactive plots so
touch/scroll gestures behave like normal UI scrolling and tapping.
"""

NON_INTERACTIVE_GRAPH_CONFIG = {
    # Strongest "disable interactivity" switch
    "staticPlot": True,
    # UX / chrome
    "displayModeBar": False,
    "displaylogo": False,
    # Interaction toggles (redundant with staticPlot, but explicit)
    "scrollZoom": False,
    "doubleClick": False,
    # Layout responsiveness
    "responsive": True,
}


