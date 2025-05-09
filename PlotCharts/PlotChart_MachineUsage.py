from Database.database_connection import db
from ChartFactory.chart_factory_MachineUasge import (
    MachineUsageChart,
)
import logging
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc

logger = logging.getLogger(__name__)

# CHART_ID = "chart-1"


def create_chart1_layout(
    default_period: str,
    dfs: dict,
    chart_id: str,
    # = CHART_ID,  # TODO: to be removed
    mobile: bool = False,
):
    """Creates the dbc.Col layout containing just the graph for chart 1."""
    chart_factory = MachineUsageChart({}, lang="zh_cn")  # Create factory instance here
    # *Desktop Chart
    if not mobile:
        initial_figure = chart_factory.create_machine_usage_chart(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            # automargin=True,
            # *taller margin
            margin=dict(l=10, r=10, t=90, b=10),
            # font=dict(size=10),
        )
        return dbc.Col(
            [
                dcc.Graph(
                    id=chart_id,
                    figure=initial_figure,
                    config={"displayModeBar": False, "responsive": True},
                    style={"width": "100%", "height": "100%", "minHeight": "25vh"},
                )
            ],
            width=4,
            className="p-2",
        )
    else:
        # *Mobile Chart
        initial_figure = chart_factory.create_machine_usage_chart_mobile_main(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            # automargin=True,
            # *taller margin
            # margin=dict(l=25, r=25, t=30, b=10),
            # font=dict(size=10),
        )
        graph_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            style={
                "height": "50%",
                "width": "85%",
            },  # Height adjusted
            config={"displayModeBar": False, "responsive": True},
        )
        return dbc.Col(
            dcc.Link(
                graph_component,
                href=f"/details/{chart_id}",  # Link using the chart ID
                id=f"link-{chart_id}",
                style={
                    "display": "block",
                    "height": "100%",
                    "width": "100%",
                },  # Ensure link covers graph
            ),
            width=4,
            className="p-0",
        )
