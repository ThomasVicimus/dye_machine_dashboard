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
        graph_component = dcc.Graph(
            id=chart_id,
            figure=initial_figure,
            style={
                "height": "20vh",
                "width": "95%",
            },  # Height adjusted
            config={"displayModeBar": False},
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


# def load_initial_chart1_data(default_period: str = "今日", mobile: bool = False):
#     """Fetches initial data and creates the first figures for chart 1."""
#     initial_figure = go.Figure().update_layout(title="Loading...")
#     placeholder_figure = go.Figure().update_layout(title="...")
#     available_periods = []

#     try:
#         conn = db.connect()
#         # Assume get_MachineUsage_data returns dict: {period: {"avg": df, "best": df, "worst": df}}
#         dfs_chart1 = get_MachineUsage_data(conn)
#         db.close(conn)

#         available_periods = list(dfs_chart1.keys())
#         # * ERROR
#         if not available_periods:
#             logger.warning("No periods found in dfs_chart1 data.")
#             initial_figure = go.Figure().update_layout(title="No Data Available")
#             placeholder_figure = initial_figure
#         elif default_period not in available_periods:
#             default_period = available_periods[0]
#             logger.error(
#                 f"Chart 1: Default period not in available periods: {default_period=}, {available_periods=}"
#             )
#             initial_figure = go.Figure().update_layout(title="Error Loading Chart 1")
#             placeholder_figure = go.Figure().update_layout(title="Error Loading Chart")
#         # * Successfully loaded data
#         else:

#             if not mobile:
#                 initial_figure = chart_factory.create_machine_usage_chart(
#                     default_period,
#                     dfs_chart1,
#                     # TODO: Pass dynamic sizes if needed
#                 )
#             else:
#                 initial_figure = chart_factory.create_machine_usage_chart_mobile_main(
#                     default_period,
#                     dfs_chart1,
#                 )
#             # Use the same figure for other placeholders initially
#             placeholder_figure = initial_figure

#     except Exception as e:
#         logger.error(
#             f"Error during initial data fetching or chart creation for Chart 1: {e}",
#             exc_info=True,
#         )
#         if "conn" in locals() and conn:  # Ensure connection is closed on error
#             db.close(conn)
#         default_period = "Error"
#         initial_figure = go.Figure().update_layout(title="Error Loading Chart 1")
#         placeholder_figure = go.Figure().update_layout(title="Error Loading Chart")

#     return initial_figure, placeholder_figure, available_periods, dfs_chart1
