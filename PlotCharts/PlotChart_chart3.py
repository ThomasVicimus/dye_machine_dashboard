from ChartFactory.chartfactory_chart3 import (
    create_chart3_figure,
    create_chart3_txt_cards,
)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import logging
from dash import html

logger = logging.getLogger(__name__)


def create_chart3_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-3",
    mobile: bool = False,
):
    """Creates the layout containing just the graph for chart 3."""
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
        return html.Div(
            [
                txtcards_layout,
                dcc.Graph(
                    id=chart_id,
                    figure=initial_figure,
                    config={"displayModeBar": False, "responsive": True},
                    style={"width": "100%", "height": "80%"},
                ),
            ],
            style={"height": "100%", "overflow": "hidden"},
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
            margin=dict(l=10, r=10, t=10, b=10),
        )
        graph_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            style={
                "height": "80%",
                "width": "100%",
            },
            config={"displayModeBar": False, "responsive": True},
        )
        return dcc.Link(
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
                "overflowY": "auto",
            },  # Ensure link covers graph
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
                    style={"height": "auto", "overflow": "hidden"},
                ),
                width=4,
            ),
            # Card 2: 4 lines, right-aligned
            dbc.Col(
                dbc.Card(
                    card2,
                    id="chart3-card-2",  # Unique ID for callbacks
                    style={"height": "auto", "overflow": "hidden"},
                ),
                width=4,
            ),
            # Card 3: 4 lines, left-aligned
            dbc.Col(
                dbc.Card(
                    card3,
                    id="chart3-card-3",  # Unique ID for callbacks
                    style={"height": "auto", "overflow": "hidden"},
                ),
                width=4,
            ),
        ],
        className="mb-0 g-2",
        style={"height": "auto"},
    )
    return three_cards_row
