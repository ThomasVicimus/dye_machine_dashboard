from ChartFactory.chart_factory_chart5 import (
    create_chart5_figure,
)
from layouts.create_buttons import create_chart5_timeframe_buttons
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html
import logging

logger = logging.getLogger(__name__)


def create_chart5_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-5",
    mobile: bool = False,
):
    """Creates the layout containing the timeframe buttons and graph for chart 5."""
    # Create the timeframe buttons
    timeframe_buttons = create_chart5_timeframe_buttons()

    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart5_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=90, b=10),
        )
        chart_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            config={"displayModeBar": False, "responsive": True},
            style={
                "width": "100%",
                "height": "100%",
                "minHeight": "30vh",
            },  # Adjusted minHeight
        )

        return html.Div(
            [timeframe_buttons, chart_component],
            style={"height": "100%", "width": "100%"},
        )

    else:
        # *Mobile Chart
        # Since there's no mobile-specific function, we'll use the same function
        # but with mobile-optimized layout settings
        initial_figure = create_chart5_figure(
            default_period,
            dfs,
            margin_top=40,
            margin_bottom=70,
            margin_left=80,  # Reduced for mobile
            margin_right=20,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            # Additional mobile optimizations can be added here if needed
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
        chart_link = dcc.Link(
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

        return html.Div(
            [timeframe_buttons, chart_link], style={"height": "100%", "width": "100%"}
        )
