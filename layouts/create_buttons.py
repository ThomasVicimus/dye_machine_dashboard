import dash_bootstrap_components as dbc
from dash import html


def create_period_button(periods, selected_period=None):
    """Creates the ButtonGroup for period selection for chart 1."""
    if not periods or periods == ["No Data"] or periods == ["Error"]:
        return dbc.Alert("No periods available", color="warning", className="mb-2")
    return dbc.ButtonGroup(
        [
            dbc.Button(
                period,
                id={"type": "period-button", "index": period},
                color="primary",
                outline=(period != selected_period) if selected_period is not None else True,
                size="sm",
                style={"fontSize": "calc(0.7rem + 0.1vw)"},
            )
            for period in periods
        ],
        className="mb-2",
    )


def create_chart5_timeframe_buttons(selected_timeframe=None):
    """Creates the ButtonGroup for timeframe selection for chart 5."""
    timeframes = ["24_hrs", "48_hrs", "72_hrs"]
    timeframe_labels = {
        "24_hrs": "24小时",
        "48_hrs": "48小时",
        "72_hrs": "72小时",
    }

    return dbc.ButtonGroup(
        [
            dbc.Button(
                timeframe_labels[timeframe],
                id={"type": "chart5-timeframe-button", "index": timeframe},
                color="primary",
                outline=(timeframe != selected_timeframe) if selected_timeframe is not None else True,
                size="sm",
                style={"fontSize": "calc(0.7rem + 0.1vw)"},
            )
            for timeframe in timeframes
        ],
        className="mb-2",
    )


def create_theme_buttons():
    """Creates colored buttons for theme selection."""
    colors = {
        # "white": {"bg": "#fdfefe", "border": "#3c3c3c"},
        "black": {"bg": "#202020", "border": "#3c3c3c"},
        "dark_blue": {"bg": "#1e3d59", "border": "#3c3c3c"},
    }

    return dbc.ButtonGroup(
        [
            dbc.Button(
                "",
                id={"type": "theme-button", "index": color_name},
                style={
                    "background-color": color_data["bg"],
                    "border-color": color_data["border"],
                    "height": "clamp(20px, 3vw, 35px)",
                    "width": "clamp(20px, 3vw, 35px)",
                },
                size="sm",
            )
            for color_name, color_data in colors.items()
        ],
        className="mb-2",
    )


# *TODO Color Theme button


def create_main_page_turner_buttons(current_page=0, total_pages=1):
    """Creates a shared Page Turner button group for the mobile main page."""
    
    # Page indicator text (e.g., "Page 1 / 5")
    # Using small font size for mobile
    page_indicator = html.Span(
        f"{current_page + 1} / {total_pages}",
        id="main-page-indicator",
        className="mx-2 align-self-center",
        style={"fontSize": "0.8rem", "color": "#fdfefe"}
    )
    
    return dbc.ButtonGroup(
        [
            dbc.Button(
                "← Prev",
                id="main-prev-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem"},
            ),
            page_indicator,
            dbc.Button(
                "Next →",
                id="main-next-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem"},
            ),
        ],
        className="mb-1",
        style={"width": "100%", "justifyContent": "center"}
    )
