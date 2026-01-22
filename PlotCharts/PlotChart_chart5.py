from ChartFactory.chart_factory_chart5 import (
    create_chart5_figure,
)
from layouts.create_buttons import create_chart5_timeframe_buttons
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html
import logging
from function.dashboard_config import get_lane_count

logger = logging.getLogger(__name__)

from function.dash_graph_config import NON_INTERACTIVE_GRAPH_CONFIG

def create_chart5_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-5",
    mobile: bool = False,
    page_size: int = None,
    mobile_page_size: int = None,
):
    """Creates the layout containing the timeframe buttons and graph for chart 5."""
    
    # Apply config defaults if not explicitly passed
    if page_size is None:
        page_size = get_lane_count("desktop")
    if mobile_page_size is None:
        mobile_page_size = get_lane_count("mobile")

    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart5_figure(
            default_period,
            dfs,
            page_size=page_size,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=90, b=10),
        )
        chart_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            config=NON_INTERACTIVE_GRAPH_CONFIG,
            style={
                "width": "100%",
                "height": "100%",
                "minHeight": "30vh",
            },  # Adjusted minHeight
        )

        return html.Div(
            [chart_component],
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
            page_size=mobile_page_size,
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
            config=NON_INTERACTIVE_GRAPH_CONFIG,
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
            # [timeframe_buttons, chart_link], style={"height": "100%", "width": "100%"}
            [chart_link],
            style={"height": "100%", "width": "100%"},
        )
