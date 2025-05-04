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


# *TODO Color Theme button
