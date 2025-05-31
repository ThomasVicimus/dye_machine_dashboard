from ChartFactory.chartfactory_chart6 import (
    create_chart6_figure,
    create_chart6_txt_cards,
)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import logging
from dash import html

logger = logging.getLogger(__name__)


def create_chart6_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-6",
    mobile: bool = False,
):
    """Creates the layout with card1 in column 1 and combined_cards+figure in column 2."""

    # Get the cards directly from the factory
    card1, combined_cards = create_chart6_txt_cards(default_period, dfs)

    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart6_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=10, b=80),  # More bottom margin for legend
            # Move legend to bottom
            legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.2,  # Position below the plot
                xanchor="center",
                x=0.5,
                font=dict(color="#fdfefe"),
            ),
        )

        # Create the combined right side (cards + figure)
        combined_fig = html.Div(
            [
                # Row 1: Combined cards
                html.Div(
                    combined_cards,
                    style={"marginBottom": "10px"},
                ),
                # Row 2: Figure (responsive)
                html.Div(
                    dcc.Graph(
                        id=chart_id,
                        figure=initial_figure,
                        config={"displayModeBar": False, "responsive": True},
                        style={"width": "100%", "height": "100%"},
                    ),
                    style={"height": "calc(100% - 80px)", "minHeight": "300px"},
                ),
            ],
            style={"height": "100%"},
        )

        # Create the main 2-column layout
        return dbc.Row(
            [
                # Column 1: Large card1
                dbc.Col(
                    dbc.Card(
                        card1,
                        id="chart6-card-1",
                        className="h-100",
                    ),
                    width=4,
                    style={"height": "100%"},
                ),
                # Column 2: Combined cards + figure
                dbc.Col(
                    combined_fig,
                    width=8,
                    style={"height": "100%"},
                ),
            ],
            className="h-100 g-2",
            style={"height": "100%"},
        )
    else:
        # *Mobile Chart
        initial_figure = create_chart6_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=10, b=80),
            # Move legend to bottom for mobile
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#fdfefe"),
            ),
        )

        # For mobile, stack everything vertically
        mobile_layout = html.Div(
            [
                # Card1
                html.Div(
                    dbc.Card(card1, className="mb-2"),
                    style={"minHeight": "150px"},
                ),
                # Combined cards
                html.Div(
                    combined_cards,
                    style={"marginBottom": "10px"},
                ),
                # Figure
                dcc.Graph(
                    id=chart_id,
                    figure=initial_figure,
                    style={
                        "height": "100%",
                        "width": "100%",
                        "minHeight": "300px",
                    },
                    config={"displayModeBar": False, "responsive": True},
                ),
            ],
            style={"height": "100%", "overflowY": "auto"},
        )

        return dcc.Link(
            mobile_layout,
            href=f"/details/{chart_id}",  # Link using the chart ID
            id=f"link-{chart_id}",
            style={
                "display": "block",
                "height": "100%",
                "width": "100%",
                "overflowY": "auto",
            },  # Ensure link covers graph
        )


def create_chart6_txtcards_layout(period, dfs):
    """
    Creates a simple 3-column layout for basic display:
    - Column 1: Large card1 (overall statistics)
    - Columns 2-3: Combined cards (card2 + card3) side by side
    """
    card1, combined_cards = create_chart6_txt_cards(period, dfs)

    # Create the layout
    cards_row = dbc.Row(
        [
            # Column 1: Large card spanning one column
            dbc.Col(
                dbc.Card(
                    card1,
                    id="chart6-card-1",  # Unique ID for callbacks
                    className="h-100",
                ),
                width=4,
            ),
            # Columns 2-3: Combined cards
            dbc.Col(
                html.Div(
                    combined_cards,
                    id="chart6-combined-cards",
                ),
                width=8,
            ),
        ],
        className="mb-0 g-2 mt-n3 mx-n3",
        style={"height": "30%"},  # Cards take 30% of the container height
    )
    return cards_row


def create_chart6_detailed_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-6-detail",
    mobile: bool = False,
):
    """
    Creates a detailed layout with 2-column structure:
    - Column 1: Large card1 (overall statistics) spanning full height
    - Column 2: Row 1 - combined cards (card2 + card3), Row 2 - main figure
    """
    card1, combined_cards = create_chart6_txt_cards(default_period, dfs)

    # Create the main figure with 2 subplots
    main_figure = create_chart6_figure(default_period, dfs)
    main_figure.update_layout(
        autosize=True,
        height=None,
        margin=dict(l=5, r=5, t=5, b=5),
    )

    # Create the combined element with cards and figure
    combined_right_side = html.Div(
        [
            # Row 1: Combined cards
            html.Div(
                combined_cards,
                style={"marginBottom": "10px"},
            ),
            # Row 2: Main figure
            html.Div(
                dcc.Graph(
                    id=f"{chart_id}-main",
                    figure=main_figure,
                    config={"displayModeBar": False, "responsive": True},
                    style={"height": "100%", "width": "100%"},
                ),
                style={"height": "calc(100% - 80px)", "minHeight": "200px"},
            ),
        ],
        style={"height": "300px"},
    )

    detailed_layout = dbc.Row(
        [
            # Column 1: Large card spanning full height
            dbc.Col(
                dbc.Card(
                    card1,
                    id="chart6-detail-card-1",
                    className="h-100",
                ),
                width=4,
                style={"height": "300px"},
            ),
            # Column 2: Combined cards + figure
            dbc.Col(
                combined_right_side,
                width=8,
                style={"height": "300px"},
            ),
        ],
        className="mb-0 g-2",
        style={"height": "300px"},
    )

    return detailed_layout
