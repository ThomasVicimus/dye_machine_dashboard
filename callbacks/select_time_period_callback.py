import dash
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback_context, ALL
import json
import logging
import pandas as pd
from Database.serialize_df import deserialize_dataframe_dict
from ChartFactory.chart_factory_MachineUasge import MachineUsageChart
from ChartFactory.chartfactory_chart3 import (
    create_chart3_figure,
    create_chart3_txt_cards,
)
from ChartFactory.chartfactory_chart4 import (
    create_chart4_figure,
    create_chart4_figure_mobile,
)
from ChartFactory.chart_factory_chart5 import create_chart5_figure
from ChartFactory.chartfactory_chart6 import (
    create_chart6_figure,
    create_chart6_figure_mobile,
    create_chart6_txt_cards,
)
import math  # Needed for ceiling division when paging machines for chart-5


logger = logging.getLogger(__name__)


# ---- Callback Registration ----


def register_chart5_timeframe_callbacks(app, mobile=False, lang: str = "zh_cn"):
    """Registers callbacks for chart5 timeframe selection."""
    CHART5_TIMEFRAME_BUTTON_TYPE = "chart5-timeframe-button"
    CHART5_TIMEFRAME_STORE_ID = "chart5-timeframe-store"
    CHART5_ID = "chart-5"

    @app.callback(
        Output(CHART5_TIMEFRAME_STORE_ID, "data"),
        Input({"type": CHART5_TIMEFRAME_BUTTON_TYPE, "index": ALL}, "n_clicks"),
        State(CHART5_TIMEFRAME_STORE_ID, "data"),
        prevent_initial_call=True,
    )
    def update_selected_chart5_timeframe(n_clicks_list, current_timeframe):
        ctx = callback_context
        if not ctx.triggered:
            return current_timeframe

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if not button_id:
            return current_timeframe

        try:
            button_info = json.loads(button_id)
            selected_timeframe = button_info.get("index")
            if selected_timeframe:
                logger.info(
                    f"Chart5 timeframe button clicked (updates {CHART5_TIMEFRAME_STORE_ID}): {selected_timeframe}"
                )
                return selected_timeframe
        except json.JSONDecodeError:
            logger.error(
                f"Failed to parse button ID for {CHART5_TIMEFRAME_STORE_ID}: {button_id}"
            )
            return current_timeframe
        return current_timeframe

    @app.callback(
        Output(CHART5_ID, "figure"),
        Input(CHART5_TIMEFRAME_STORE_ID, "data"),
        Input("all-chart-data-store", "data"),
        Input(
            "chart-2-interval", "n_intervals"
        ),  # reuse existing timer for auto page turning
        prevent_initial_call=True,
    )
    def update_chart5_figure(selected_timeframe, all_chart_data, n_intervals):
        # Get the chart5 specific data from all_chart_data
        chart5_data_serialized = all_chart_data.get(f"{CHART5_ID}-data-store")

        if not chart5_data_serialized:
            logger.warning(
                f"Chart5: No data found in store key '{CHART5_ID}-data-store'"
            )
            return go.Figure().update_layout(title="Chart5: No data available")

        logger.info(
            f"Chart5: Serialized data received: {chart5_data_serialized.keys()}"
        )

        # Deserialize the chart5 data
        deserialized_chart5_data = None
        try:
            deserialized_chart5_data = deserialize_dataframe_dict(
                chart5_data_serialized
            )
            logger.info("Chart5: Deserialization successful.")
            logger.debug(
                f"Chart5: Deserialized data: {deserialized_chart5_data.keys()}"
            )
        except Exception as e:
            logger.error(
                f"Chart5: Exception during deserialization for store key '{CHART5_ID}-data-store': {e}",
                exc_info=True,
            )

        logger.info(
            f"Chart5: Updating figure for timeframe: {selected_timeframe} using initially loaded data."
        )

        # Handle cases where data loading or deserialization failed
        if deserialized_chart5_data is None or (
            isinstance(deserialized_chart5_data, dict)
            and "error" in deserialized_chart5_data
        ):
            error_msg_detail = (
                "Deserialization resulted in None"
                if deserialized_chart5_data is None
                else deserialized_chart5_data.get(
                    "error", "Unknown deserialization error"
                )
            )
            error_msg = (
                deserialized_chart5_data.get(
                    "error", "Initial data load or deserialization failed"
                )
                if isinstance(deserialized_chart5_data, dict)
                else "Initial data load or deserialization failed"
            )
            logger.warning(
                f"Chart5: Cannot update figure. Reason: {error_msg_detail}. Serialized data was: {chart5_data_serialized}"
            )
            return go.Figure().update_layout(title=f"Chart5 Error: {error_msg}")

        try:
            # ---------------- Pagination-by-slicing logic ----------------
            PAGE_SIZE = 6

            # Safely extract the raw dataframe for the currently selected timeframe
            df_all = deserialized_chart5_data.get(selected_timeframe, {}).get(
                "all_machine"
            )

            if df_all is not None and not df_all.empty:
                unique_machines = df_all["machine_name"].unique().tolist()

                page_count = max(1, math.ceil(len(unique_machines) / PAGE_SIZE))

                # n_intervals may be None when the callback fires from timeframe button change
                current_interval = n_intervals or 0
                current_page_idx = current_interval % page_count

                start_idx = current_page_idx * PAGE_SIZE
                end_idx = start_idx + PAGE_SIZE
                machines_subset = unique_machines[start_idx:end_idx]

                df_subset = df_all[df_all["machine_name"].isin(machines_subset)].copy()

                # Build a minimal data structure expected by chart factory
                data_for_fig = {selected_timeframe: {"all_machine": df_subset}}
            else:
                # Fall back to original data if dataframe missing/empty
                data_for_fig = deserialized_chart5_data

            # -------------------------------------------------------------

            if mobile:
                # For mobile, use mobile-optimized parameters
                new_figure = create_chart5_figure(
                    selected_timeframe,
                    data_for_fig,
                    lang=lang,
                    margin_top=40,
                    margin_bottom=70,
                    margin_left=80,
                    margin_right=20,
                )
            else:
                # For desktop
                new_figure = create_chart5_figure(
                    selected_timeframe,
                    data_for_fig,
                    lang=lang,
                )
                # Apply consistent layout updates
                new_figure.update_layout(
                    autosize=True,
                    height=None,
                    margin=dict(l=10, r=10, t=90, b=10),
                )
            return new_figure

        except Exception as e:
            logger.error(
                f"Chart5: Error generating figure for timeframe {selected_timeframe}: {e}",
                exc_info=True,
            )
            return go.Figure().update_layout(
                title=f"Chart5: Error generating chart for {selected_timeframe}"
            )

    logger.info("Chart5 timeframe callbacks registered.")


def register_time_period_callbacks(app, mobile=False, lang: str = "zh_cn"):
    charts_var = {
        "chart-1": {
            "CHART_ID": "chart-1",
            "chart_factory_desktop": MachineUsageChart(
                {}, lang=lang
            ).create_machine_usage_chart,
            "chart_factory_mobile": MachineUsageChart(
                {}, lang=lang
            ).create_machine_usage_chart_mobile_main,
            "chart_titles": "Machine Usage",
            "margin": dict(l=10, r=10, t=55, b=10),
        },
        # "chart-2": {
        #     "CHART_ID": "chart-2",
        #     "chart_factory": MachineUsageChart(
        #         {}, lang=lang
        #     ).create_machine_usage_chart,
        #     "chart_titles": "Machine Usage 2",
        # },
        "chart-3": {
            "CHART_ID": "chart-3",
            "chart_factory_desktop": create_chart3_figure,
            "chart_factory_mobile": create_chart3_figure,
            "chart_titles": "Production Volume",
            "margin": dict(l=10, r=10, t=10, b=10),
        },
        "chart-4": {
            "CHART_ID": "chart-4",
            "chart_factory_desktop": create_chart4_figure,
            "chart_factory_mobile": create_chart4_figure_mobile,
            "chart_titles": "Machine Waste",
            "margin": dict(l=10, r=10, t=55, b=10),
        },
        "chart-6": {
            "CHART_ID": "chart-6",
            "chart_factory_desktop": create_chart6_figure,
            "chart_factory_mobile": create_chart6_figure_mobile,
            "chart_titles": "Idle Time",
            "margin": dict(l=10, r=10, t=10, b=80),
        },
    }

    """Registers callbacks for all charts defined in charts_var."""
    PERIOD_BUTTON_TYPE = "period-button"
    PERIOD_STORE_ID = "time-period-store"

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
                # Log which button triggered this, though it updates a global store
                logger.info(
                    f"Period button clicked (updates {PERIOD_STORE_ID}): {selected_period}"
                )
                return selected_period
        except json.JSONDecodeError:
            logger.error(
                f"Failed to parse button ID for {PERIOD_STORE_ID}: {button_id}"
            )
            return current_period
        return current_period

    # Register callbacks for each chart in charts_var
    for chart_id, chart_config in charts_var.items():
        CHART_ID = chart_config["CHART_ID"]
        current_chart_margin = chart_config[
            "margin"
        ]  # Extract margin for the current chart
        if mobile:
            chart_factory = chart_config["chart_factory_mobile"]
        else:
            chart_factory = chart_config["chart_factory_desktop"]

        @app.callback(
            Output(CHART_ID, "figure"),
            Input(PERIOD_STORE_ID, "data"),
            Input("all-chart-data-store", "data"),
            prevent_initial_call=True,
        )
        def update_chart_figure(
            selected_period,
            all_chart_data,
            chart_id=CHART_ID,
            chart_factory=chart_factory,
            margin=current_chart_margin,  # Pass the specific margin as a default argument
        ):
            # Get the specific chart's data from all_chart_data
            chart_specific_data_serialized = all_chart_data.get(
                f"{chart_id}-data-store"  # Use chart_id from the function's default argument
            )

            logger.info(
                f"Chart {chart_id}: Serialized data received: {chart_specific_data_serialized.keys()}"
            )

            # Deserialize the specific chart's data
            deserialized_chart_data = None  # Initialize to None
            try:
                deserialized_chart_data = deserialize_dataframe_dict(
                    chart_specific_data_serialized
                )
                logger.info(f"Chart {chart_id}: Deserialization successful.")
                logger.debug(
                    f"Chart {chart_id}: Deserialized data: {deserialized_chart_data.keys()}"
                )
            except Exception as e:
                logger.error(
                    f'Chart {chart_id}: Exception during deserialization for store key f"{chart_id}-data-store": {e}',
                    exc_info=True,
                )
                # Keep deserialized_chart_data as None or an error structure if preferred
                # For now, it will remain None, and the existing error handling below will catch it.

            logger.info(
                f"Chart {chart_id}: Updating figure for period: {selected_period} using initially loaded data."
            )
            logger.debug(
                f"Chart {chart_id}: Deserialized data: {deserialized_chart_data}"
            )

            # Handle cases where initial data loading might have failed or deserialization failed
            if deserialized_chart_data is None or (
                isinstance(deserialized_chart_data, dict)
                and "error" in deserialized_chart_data
            ):
                error_msg_detail = (
                    "Deserialization resulted in None"
                    if deserialized_chart_data is None
                    else deserialized_chart_data.get(
                        "error", "Unknown deserialization error"
                    )
                )
                error_msg = (
                    deserialized_chart_data.get(
                        "error", "Initial data load or deserialization failed"
                    )
                    if isinstance(deserialized_chart_data, dict)
                    else "Initial data load or deserialization failed"
                )
                logger.warning(
                    f"Chart {chart_id}: Cannot update figure. Reason: {error_msg_detail}. Serialized data was: {chart_specific_data_serialized}"
                )
                logger.warning(
                    f"Chart {chart_id}: Cannot update figure, data unavailable. Msg: {error_msg}"
                )
                return go.Figure().update_layout(title=f"Error: {error_msg}")

            # # Handle cases where the selected period itself is invalid
            # if not selected_period or selected_period in ["No Data", "Error"]:
            #     logger.warning(
            #         f"Chart {chart_id}: Invalid period selected: {selected_period}"
            #     )
            #     return go.Figure().update_layout(
            #         title=f"Invalid Period Selected: {selected_period}"
            #     )

            # # Check if the selected period exists within the chart data
            # if selected_period not in deserialized_chart_data:
            #     logger.warning(
            #         f"Chart {chart_id}: Selected period '{selected_period}' not found in data for chart {chart_id}."
            #     )
            #     available_periods = list(deserialized_chart_data.keys())
            #     return go.Figure().update_layout(
            #         title=f"Data not found for period {selected_period}. Available periods: {available_periods}"
            #     )

            try:
                if mobile:
                    new_figure = chart_factory(  # Use chart_factory from the function's default argument
                        selected_period,
                        deserialized_chart_data,  # Pass the chart-specific deserialized dataset
                    )
                    # No additional layout updates for mobile to preserve default styling
                else:
                    # Create the chart using the deserialized data and the selected period
                    new_figure = chart_factory(  # Use chart_factory from the function's default argument
                        selected_period,
                        deserialized_chart_data,  # Pass the chart-specific deserialized dataset
                    )
                    # Match exact layout update as in create_chart1_layout
                    new_figure.update_layout(
                        autosize=True,
                        height=None,
                        margin=margin,  # Use the captured margin
                    )
                    # Ensure legend placement for chart-6 matches the initial configuration
                    if chart_id == "chart-6":
                        new_figure.update_layout(
                            legend=dict(
                                orientation="h",
                                yanchor="top",
                                y=-0.2,  # Match initial layout legend position
                                xanchor="center",
                                x=0.5,
                                font=dict(color="#fdfefe"),
                            )
                        )
                return new_figure

            except Exception as e:
                logger.error(
                    f"Chart {chart_id}: Error generating figure for period {selected_period} from initial data: {e}",
                    exc_info=True,
                )
                return go.Figure().update_layout(
                    title=f"Error generating chart for {selected_period}"
                )

        logger.info(
            f"Chart {CHART_ID} callbacks registered (using initially loaded data)."
        )


def register_txt_cards_callbacks(app, mobile=False, lang: str = "zh_cn"):
    """Registers callbacks for updating text cards when time period changes."""
    PERIOD_STORE_ID = "time-period-store"

    # Configuration for charts with text cards
    txt_cards_config = {
        "chart-3": {
            "card_ids": ["chart3-card-1", "chart3-card-2", "chart3-card-3"],
            "card_factory": create_chart3_txt_cards,
            "num_cards": 3,
        },
        "chart-6": {
            "card_ids": ["chart6-card-1"],  # Only chart6-card-1 exists in the layout
            "card_factory": create_chart6_txt_cards,
            "num_cards": 1,  # Only updating 1 card (the large card1)
        },
    }

    # Register callbacks for each chart's text cards
    for chart_id, config in txt_cards_config.items():
        card_factory = config["card_factory"]
        card_ids = config["card_ids"]
        num_cards = config["num_cards"]

        @app.callback(
            [Output(card_id, "children") for card_id in card_ids],
            Input(PERIOD_STORE_ID, "data"),
            Input("all-chart-data-store", "data"),
            prevent_initial_call=True,
        )
        def update_txt_cards(
            selected_period,
            all_chart_data,
            chart_id=chart_id,
            card_factory=card_factory,
            num_cards=num_cards,
        ):
            # Get the specific chart's data from all_chart_data
            chart_specific_data_serialized = all_chart_data.get(
                f"{chart_id}-data-store"
            )

            if not chart_specific_data_serialized:
                logger.warning(
                    f"Cards {chart_id}: No data found in store key '{chart_id}-data-store'"
                )
                error_card = html.Div("No data available")
                return [error_card] * num_cards

            logger.info(
                f"Cards {chart_id}: Serialized data received: {chart_specific_data_serialized.keys()}"
            )

            # Deserialize the specific chart's data
            deserialized_chart_data = None
            try:
                deserialized_chart_data = deserialize_dataframe_dict(
                    chart_specific_data_serialized
                )
                logger.info(f"Cards {chart_id}: Deserialization successful.")
                logger.debug(
                    f"Cards {chart_id}: Deserialized data: {deserialized_chart_data.keys()}"
                )
            except Exception as e:
                logger.error(
                    f'Cards {chart_id}: Exception during deserialization for store key "{chart_id}-data-store": {e}',
                    exc_info=True,
                )

            logger.info(
                f"Cards {chart_id}: Updating cards for period: {selected_period} using initially loaded data."
            )

            # Handle cases where initial data loading might have failed or deserialization failed
            if deserialized_chart_data is None or (
                isinstance(deserialized_chart_data, dict)
                and "error" in deserialized_chart_data
            ):
                error_msg_detail = (
                    "Deserialization resulted in None"
                    if deserialized_chart_data is None
                    else deserialized_chart_data.get(
                        "error", "Unknown deserialization error"
                    )
                )
                error_msg = (
                    deserialized_chart_data.get(
                        "error", "Initial data load or deserialization failed"
                    )
                    if isinstance(deserialized_chart_data, dict)
                    else "Initial data load or deserialization failed"
                )
                logger.warning(
                    f"Cards {chart_id}: Cannot update cards. Reason: {error_msg_detail}. Serialized data was: {chart_specific_data_serialized}"
                )
                error_card = html.Div(f"Error: {error_msg}")
                return [error_card] * num_cards

            try:
                # Create the updated cards using the deserialized data and the selected period
                updated_cards = card_factory(
                    selected_period,
                    deserialized_chart_data,
                )

                # Handle chart-6 special case: factory returns 2 cards but we only update 1
                if chart_id == "chart-6":
                    # Return only the first card (card1 - the large overview card)
                    return [updated_cards[0]]
                else:
                    # Return all cards as a list (they come as tuple from factory functions)
                    return list(updated_cards)

            except Exception as e:
                logger.error(
                    f"Cards {chart_id}: Error generating cards for period {selected_period} from initial data: {e}",
                    exc_info=True,
                )
                error_card = html.Div(f"Error generating cards for {selected_period}")
                return [error_card] * num_cards

        logger.info(
            f"Cards {chart_id} callbacks registered (using initially loaded data)."
        )


def register_auto_refresh_callbacks(app, mobile=False, lang: str = "zh_cn"):
    """Registers callbacks for automatic refresh of the data store every 60 seconds.
    The existing callbacks will automatically update charts and text cards when the data store changes.
    """
    from Database.fetch_all_charts_data import get_all_charts_data
    from Database.database_connection import db
    from Database.serialize_df import serialize_dataframe_dict

    INTERVAL_ID = "mobile-interval"
    ALL_CHART_DATA_STORE_ID = "all-chart-data-store"

    @app.callback(
        # Only update the data store - let existing callbacks handle UI updates
        Output(ALL_CHART_DATA_STORE_ID, "data"),
        Input(INTERVAL_ID, "n_intervals"),
        prevent_initial_call=True,
    )
    def auto_refresh_data_store(n_intervals):
        """Auto refresh the data store with fresh data from database every 60 seconds.
        This will trigger all existing callbacks to update their respective components.
        """
        logger.info(f"Auto refresh triggered - interval {n_intervals}")

        try:
            # Fetch fresh data from database
            fresh_charts_data = get_all_charts_data(db)

            # Serialize the fresh data for storage
            serialized_fresh_data = {
                key: serialize_dataframe_dict(df)
                for key, df in fresh_charts_data.items()
            }

            logger.info("Fresh data fetched and serialized successfully")
            logger.info(
                "Data store updated - existing callbacks will handle UI updates"
            )

            return serialized_fresh_data

        except Exception as e:
            logger.error(
                f"Auto refresh: Critical error during data fetch: {e}", exc_info=True
            )

            # Keep the existing data in store (don't update it)
            from dash import no_update

            return no_update

    logger.info("Auto refresh data store callback registered.")


def register_chart2_data_refresh_callback(app, mobile=False, lang: str = "zh_cn"):
    """Registers callback for chart-2 DataTable data refresh when data store changes."""

    @app.callback(
        [Output("chart-2", "data"), Output("chart-2", "columns")],
        Input("all-chart-data-store", "data"),
        prevent_initial_call=True,
    )
    def update_chart2_data(all_chart_data):
        """Update chart-2 DataTable data and columns when data store changes."""
        try:
            # Get chart-2 data from the store
            chart2_data_serialized = all_chart_data.get("chart-2-data-store")

            if not chart2_data_serialized:
                logger.warning("Chart2 data refresh: No data found in store")
                return [], []

            # Deserialize the data
            chart2_data = deserialize_dataframe_dict(chart2_data_serialized)

            # Get the appropriate data for mobile/desktop
            mobile_option = "mobile" if mobile else "desktop"
            df = chart2_data.get(mobile_option, {}).get("all_machine", None)

            if df is None or df.empty:
                logger.warning("Chart2 data refresh: Empty dataframe")
                return [], []

            # Convert to table format
            table_data = df.to_dict("records")
            table_columns = [{"name": i, "id": i} for i in df.columns]

            logger.info("Chart2 data refresh: Successfully updated data and columns")
            return table_data, table_columns

        except Exception as e:
            logger.error(
                f"Chart2 data refresh: Error updating data: {e}", exc_info=True
            )
            return [], []

    logger.info("Chart2 data refresh callback registered.")
