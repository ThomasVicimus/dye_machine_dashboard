import dash_bootstrap_components as dbc
from dash import html


def create_period_button(periods, selected_period=None):
    """
    [DEPRECATED] Creates the ButtonGroup for period selection for chart 1.
    This function is deprecated in favor of create_combined_control_row.
    """
    if not periods or periods == ["No Data"] or periods == ["Error"]:
        return dbc.Alert("No periods available", color="warning", className="mb-2")
    return dbc.ButtonGroup(
        [
            dbc.Button(
                period,
                id={"type": "period-button", "index": period},
                color="primary",
                outline=(
                    (period != selected_period) if selected_period is not None else True
                ),
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
                outline=(
                    (timeframe != selected_timeframe)
                    if selected_timeframe is not None
                    else True
                ),
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
    """
    [DEPRECATED] Creates a shared Page Turner button group for the mobile main page.
    This function is deprecated in favor of create_combined_control_row.
    """

    # Page indicator text (e.g., "Page 1 / 5")
    # Using small font size for mobile
    page_indicator = html.Span(
        f"{current_page + 1} / {total_pages}",
        id="main-page-indicator",
        className="mx-2 align-self-center",
        style={"fontSize": "0.8rem", "color": "#fdfefe"},
    )

    return dbc.ButtonGroup(
        [
            dbc.Button(
                "←-",
                id="main-prev-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem"},
            ),
            page_indicator,
            dbc.Button(
                "-→",
                id="main-next-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem"},
            ),
        ],
        className="mb-1",
        style={"width": "100%", "justifyContent": "center"},
    )


def create_combined_control_row(periods, selected_period=None, current_page=0, total_pages=1):
    """
    Creates a combined row containing Time Period buttons (Left) and Page Turner buttons (Right).
    This replaces the separate calls to keep the UI compact.
    """
    
    # --- Part 1: Period Buttons ---
    period_buttons_content = None
    if not periods or periods == ["No Data"] or periods == ["Error"]:
        period_buttons_content = dbc.Alert("No periods", color="warning", className="mb-0 py-1", style={"fontSize": "0.7rem"})
    else:
        period_buttons_content = dbc.ButtonGroup(
            [
                dbc.Button(
                    period,
                    id={"type": "period-button", "index": period},
                    color="primary",
                    outline=(
                        (period != selected_period) if selected_period is not None else True
                    ),
                    size="sm",
                    style={"fontSize": "0.7rem", "padding": "0.1rem 0.3rem"},
                )
                for period in periods
            ],
            className="mb-0",
        )

    # --- Part 2: Page Turner Buttons ---
    # Page indicator text (e.g., "1/5")
    page_indicator = html.Span(
        f"{current_page + 1}/{total_pages}",
        id="main-page-indicator",
        className="mx-1 align-self-center",
        style={"fontSize": "0.7rem", "color": "#fdfefe", "whiteSpace": "nowrap"},
    )

    page_turner_content = dbc.ButtonGroup(
        [
            dbc.Button(
                "←",
                id="main-prev-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem", "padding": "0.1rem 0.3rem"},
            ),
            page_indicator,
            dbc.Button(
                "→",
                id="main-next-button",
                color="secondary",
                outline=True,
                size="sm",
                style={"fontSize": "0.7rem", "padding": "0.1rem 0.3rem"},
            ),
        ],
        className="mb-0",
    )

    # --- Combined Row ---
    return dbc.Row(
        [
            dbc.Col(
                period_buttons_content,
                width=True, # Auto width
                className="d-flex align-items-center justify-content-start",
                style={"overflowX": "auto", "paddingRight": "5px"}
            ),
            dbc.Col(
                page_turner_content,
                width="auto", # Fit content
                className="d-flex align-items-center justify-content-end",
                style={"paddingLeft": "5px"}
            ),
        ],
        className="g-0 w-100",
        align="center",
        style={"flexWrap": "nowrap"} # Prevent wrapping to keep single line
    )
