import dash_bootstrap_components as dbc
from dash import html, dcc


def create_mobile_detail_header(
    *,
    chart_title: str,
    header_right=None,
    back_href: str = "/",
):
    """Header row for the mobile detail overlay.

    Layout:
    - Left: Back button
    - Center: Title
    - Right: Optional button group (e.g., period/timeframe buttons)
    """
    return dbc.Row(
        [
            dbc.Col(
                dcc.Link(
                    "Back",
                    href=back_href,
                    className="btn btn-secondary btn-sm",
                ),
                width="auto",
            ),
            dbc.Col(
                html.H4(
                    chart_title,
                    className="text-white text-center mb-0",
                ),
                width=True,
            ),
            dbc.Col(
                header_right if header_right is not None else html.Div(),
                width="auto",
                className="d-flex justify-content-end",
            ),
        ],
        align="center",
        className="mb-2",
    )


def create_mobile_detail_overlay_layout(
    *,
    chart_id: str,
    chart_title: str,
    graphs_container,
    header_right=None,
):
    """Full-screen mobile detail overlay wrapper used by detail routing callbacks."""
    return html.Div(
        id=f"mobile-detail-wrapper-{chart_id}",
        style={
            "width": "100vw",
            "height": "100vh",
            "overflowY": "auto",
            "overflowX": "hidden",
            "position": "relative",
            "backgroundColor": "#000000",
            "zIndex": 1000,
        },
        children=[
            dbc.Container(
                id=f"mobile-rotated-detail-content-{chart_id}",
                children=[
                    create_mobile_detail_header(
                        chart_title=chart_title,
                        header_right=header_right,
                    ),
                    graphs_container,
                ],
                fluid=True,
            )
        ],
    )


