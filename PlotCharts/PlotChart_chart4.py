from ChartFactory.chartfactory_chart4 import (
    create_chart4_figure,
    create_chart4_figure_mobile,
)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import logging

logger = logging.getLogger(__name__)


def create_chart4_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-4",
    mobile: bool = False,
):
    """Creates the layout containing just the graph for chart 4."""
    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart4_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=90, b=10),
        )
        return dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            config={"displayModeBar": False, "responsive": True},
            style={
                "width": "100%",
                "height": "100%",
                "minHeight": "30vh",
            },  # Adjusted minHeight
        )
    else:
        # *Mobile Chart
        initial_figure = create_chart4_figure_mobile(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            # Margins are handled by create_chart4_figure_mobile, but can be overridden if needed
            # margin=dict(l=20, r=20, t=40, b=70),
        )
        graph_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            style={
                "height": "100%",
                "width": "100%",
                "minHeight": "30vh",  # Adjusted minHeight
            },
            config={"displayModeBar": False, "responsive": True},
        )
        return dcc.Link(
            graph_component,
            href=f"/details/{chart_id}",  # Link using the chart ID
            id=f"link-{chart_id}",
            style={
                "display": "block",
                "height": "100%",
                "width": "100%",
                "minHeight": "30vh",  # Ensure link covers graph
            },
        )
