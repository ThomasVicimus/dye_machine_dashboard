from Database.database_connection import db
from ChartFactory.chart_factory_MachineUasge import (
    MachineUsageChart,
    get_MachineUsage_data,
)
import logging
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


def load_initial_chart1_data(default_period: str = "今日", mobile: bool = False):
    """Fetches initial data and creates the first figures for chart 1."""
    initial_figure = go.Figure().update_layout(title="Loading...")
    placeholder_figure = go.Figure().update_layout(title="...")
    available_periods = []

    try:
        conn = db.connect()
        # Assume get_MachineUsage_data returns dict: {period: {"avg": df, "best": df, "worst": df}}
        dfs_chart1 = get_MachineUsage_data(conn)
        db.close(conn)

        available_periods = list(dfs_chart1.keys())
        # * ERROR
        if not available_periods:
            logger.warning("No periods found in dfs_chart1 data.")
            default_period = "No Data"
            initial_figure = go.Figure().update_layout(title="No Data Available")
            placeholder_figure = initial_figure
        elif default_period not in available_periods:
            default_period = available_periods[0]
            logger.error(
                f"Chart 1: Default period not in available periods: {default_period=}, {available_periods=}"
            )
            default_period = "Error"
            initial_figure = go.Figure().update_layout(title="Error Loading Chart 1")
            placeholder_figure = go.Figure().update_layout(title="Error Loading Chart")
        # * Successfully loaded data
        else:

            chart_factory = MachineUsageChart(
                {}, lang="zh_cn"
            )  # Create factory instance here
            if not mobile:
                initial_figure = chart_factory.create_machine_usage_chart(
                    default_period,
                    dfs_chart1,
                    # TODO: Pass dynamic sizes if needed
                )
            else:
                initial_figure = chart_factory.create_machine_usage_chart_mobile_main(
                    default_period,
                    dfs_chart1,
                )
            # Use the same figure for other placeholders initially
            placeholder_figure = initial_figure

    except Exception as e:
        logger.error(
            f"Error during initial data fetching or chart creation for Chart 1: {e}",
            exc_info=True,
        )
        if "conn" in locals() and conn:  # Ensure connection is closed on error
            db.close(conn)
        default_period = "Error"
        initial_figure = go.Figure().update_layout(title="Error Loading Chart 1")
        placeholder_figure = go.Figure().update_layout(title="Error Loading Chart")

    return initial_figure, placeholder_figure, available_periods, default_period
