import dash
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback_context, ALL
import json
import logging
import pandas as pd  # Add pandas import
from Database.serialize_df import deserialize_dataframe_dict

# import pandas as pd # Add if DataFrame reconstruction is needed later

from database_connection import db
from chart_factory_MachineUasge import MachineUsageChart, get_MachineUsage_data

logger = logging.getLogger(__name__)


# ---- Callback Registration ----


def register_time_period_callbacks(app, chart_id, mobile=False, lang: str = "zh_cn"):
    """Registers callbacks for chart 1 interactivity."""
    # define var for each chart
    PERIOD_BUTTON_TYPE = "period-button"
    PERIOD_STORE_ID = "time-period-store"
    charts_var = {
        "chart-1": {
            "CHART_ID": "chart-1",
            "CHART_DATA_STORE_ID": "chart1-data-store",
            "chart_factory": MachineUsageChart(
                {}, lang=lang
            ),  # Create factory instance for callbacks
        },
        # "chart2": {
        #     "CHART_ID": "chart-2",
        #     "PERIOD_STORE_ID": "selected-period-store-chart2",
        #     "CHART_DATA_STORE_ID": "chart2-data-store",
        #     "PERIOD_BUTTON_TYPE": "period-button",
        # },
    }

    CHART_ID = charts_var[chart_id]["CHART_ID"]
    CHART_DATA_STORE_ID = charts_var[chart_id]["CHART_DATA_STORE_ID"]
    chart_factory = charts_var[chart_id]["chart_factory"]

    # chart_factory = MachineUsageChart(
    #     {}, lang="zh_cn"
    # )  # Create factory instance for callbacks

    @app.callback(
        Output(PERIOD_STORE_ID, "data"),
        Input({"type": PERIOD_BUTTON_TYPE, "index": ALL}, "n_clicks"),
        State(PERIOD_STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_selected_period(n_clicks_list, current_period):
        ctx = callback_context
        if not ctx.triggered:
            return current_period

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not button_id:
            return current_period

        try:
            button_info = json.loads(button_id)
            selected_period = button_info.get("index")
            if selected_period:
                logger.info(
                    f"Chart {CHART_ID}: Period button clicked: {selected_period}"
                )
                return selected_period
        except json.JSONDecodeError:
            logger.error(f"Chart {CHART_ID}: Failed to parse button ID: {button_id}")
            return current_period

        return current_period

    @app.callback(
        Output(CHART_ID, "figure"),
        # Trigger directly by period selection AND read data from the store
        Input(PERIOD_STORE_ID, "data"),
        Input(CHART_DATA_STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_chart_figure(selected_period, chart_data):
        # Deserialize the data from the store first
        deserialized_chart_data = deserialize_dataframe_dict(chart_data)

        # chart1_data now holds the full dataset loaded at startup
        # selected_period is the newly chosen period
        logger.info(
            f"Chart {CHART_ID}: Updating figure for period: {selected_period} using initially loaded data."
        )

        # Handle cases where initial data loading might have failed or deserialization failed
        if deserialized_chart_data is None or (
            isinstance(deserialized_chart_data, dict)
            and "error" in deserialized_chart_data
        ):
            error_msg = (
                deserialized_chart_data.get(
                    "error", "Initial data load or deserialization failed"
                )
                if isinstance(deserialized_chart_data, dict)
                else "Initial data load or deserialization failed"
            )
            logger.warning(
                f"Chart {CHART_ID}: Cannot update figure, data unavailable. Msg: {error_msg}"
            )
            return go.Figure().update_layout(title=f"Error: {error_msg}")

        # Handle cases where the selected period itself is invalid
        if not selected_period or selected_period in ["No Data", "Error"]:
            logger.warning(
                f"Chart {CHART_ID}: Invalid period selected: {selected_period}"
            )
            return go.Figure().update_layout(
                title=f"Invalid Period Selected: {selected_period}"
            )

        # Data is pre-fetched and now deserialized in deserialized_chart_data
        dfs_update = deserialized_chart_data  # Use the deserialized data

        # Check if the selected period exists within the deserialized data
        if selected_period not in dfs_update:
            logger.warning(
                f"Chart {CHART_ID}: Selected period '{selected_period}' not found in initially loaded data."
            )
            # Attempt to find available periods from the loaded data for a better error message
            available_periods = (
                list(dfs_update.keys()) if isinstance(dfs_update, dict) else []
            )
            return go.Figure().update_layout(
                title=f"Data not found for {selected_period}. Available: {available_periods}"
            )

        try:
            if mobile:
                new_figure = chart_factory.create_machine_usage_chart_mobile_main(
                    selected_period,
                    dfs_update,  # Pass the deserialized dataset
                )
            else:
                # Create the chart using the deserialized data and the selected period
                new_figure = chart_factory.create_machine_usage_chart(
                    selected_period,
                    dfs_update,  # Pass the deserialized dataset
                )
            return new_figure

        except Exception as e:
            logger.error(
                f"Chart {CHART_ID}: Error generating figure for period {selected_period} from initial data: {e}",
                exc_info=True,
            )
            return go.Figure().update_layout(
                title=f"Error generating chart for {selected_period}"
            )

    logger.info(f"Chart {CHART_ID} callbacks registered (using initially loaded data).")
