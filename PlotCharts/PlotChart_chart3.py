from ChartFactory.chartfactory_chart3 import (
    create_chart3_figure,
    create_chart3_txt_cards,
)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import logging

logger = logging.getLogger(__name__)


def create_chart3_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-3",
    mobile: bool = False,
):
    """Creates the dbc.Col layout containing just the graph for chart 3."""
    txtcards_layout = create_chart3_txtcards_layout(default_period, dfs)
    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart3_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        return dbc.Col(
            [
                txtcards_layout,
                dcc.Graph(
                    id=chart_id,
                    figure=initial_figure,
                    config={"displayModeBar": False, "responsive": True},
                    style={"width": "100%", "height": "100%", "minHeight": "30vh"},
                ),
            ],
            width=4,
            className="px-2",
        )
    else:
        # *Mobile Chart
        initial_figure = create_chart3_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
        )
        graph_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            style={
                "height": "100%",
                "width": "100%",
                "minHeight": "20vh",
            },
            config={"displayModeBar": False, "responsive": True},
        )
        return dbc.Col(
            dcc.Link(
                [
                    txtcards_layout,
                    graph_component,
                ],
                href=f"/details/{chart_id}",  # Link using the chart ID
                id=f"link-{chart_id}",
                style={
                    "display": "block",
                    "height": "100%",
                    "width": "100%",
                    "minHeight": "20vh",
                },  # Ensure link covers graph
            ),
            width=4,
            className="p-0",
        )


def create_chart3_txtcards_layout(period, dfs):
    card1, card2, card3 = create_chart3_txt_cards(period, dfs)
    three_cards_row = dbc.Row(
        [
            # Card 1: 2 lines, center-aligned
            dbc.Col(
                dbc.Card(
                    card1,
                    id="chart3-card-1",  # Unique ID for callbacks
                    className="h-100",
                ),
                width=4,
            ),
            # Card 2: 4 lines, right-aligned
            dbc.Col(
                dbc.Card(
                    card2,
                    id="chart3-card-2",  # Unique ID for callbacks
                    className="h-100",
                ),
                width=4,
            ),
            # Card 3: 4 lines, left-aligned
            dbc.Col(
                dbc.Card(
                    card3,
                    id="chart3-card-3",  # Unique ID for callbacks
                    className="h-100",
                ),
                width=4,
            ),
        ],
        className="mb-0 g-2",
    )
    return three_cards_row
