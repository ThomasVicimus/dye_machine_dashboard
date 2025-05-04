import dash_bootstrap_components as dbc


def create_period_button(periods):
    """Creates the ButtonGroup for period selection for chart 1."""
    if not periods or periods == ["No Data"] or periods == ["Error"]:
        return dbc.Alert("No periods available", color="warning", className="mb-2")
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
                    "height": "30px",
                    "width": "30px",
                },
                size="sm",
            )
            for color_name, color_data in colors.items()
        ],
        className="mb-2",
    )


# *TODO Color Theme button
