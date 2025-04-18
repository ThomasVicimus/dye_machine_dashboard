import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MachineUsageChart:
    def __init__(self, dfs: Dict[str, Dict[str, pd.DataFrame]]):
        """
        Initialize the chart factory with the dataframes containing machine usage data.

        Args:
            dfs: Dictionary containing dataframes for different charts
        """
        self.dfs = dfs
        self.colors = [
            "#2ecc71",
            "#f1c40f",
            "#e74c3c",
            "#3498db",
        ]  # Green, Yellow, Red, Blue

    def create_pie_chart(self, df: pd.DataFrame, title: str) -> go.Pie:
        """
        Create a single pie chart trace.

        Args:
            df: DataFrame containing the data
            title: Title for the pie chart

        Returns:
            plotly.graph_objects.Pie: The pie chart trace
        """
        try:
            # Log the input data for debugging
            logger.debug(f"Creating pie chart for {title}")
            logger.debug(f"Input DataFrame shape: {df.shape}")
            logger.debug(f"Input DataFrame columns: {df.columns.tolist()}")
            logger.debug(
                f"Input DataFrame values: {df[['run', 'idle', 'down', 'repair']].values}"
            )

            # Ensure we have the required columns
            required_columns = ["run", "idle", "down", "repair"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError(
                    f"Missing required columns. Expected: {required_columns}, Got: {df.columns.tolist()}"
                )

            # Get values as a list
            values = df[required_columns].values[0].tolist()
            labels = ["Running", "Idle", "Down", "Repair"]

            # Log the values being used
            logger.debug(f"Values for pie chart: {values}")
            logger.debug(f"Type of values: {type(values)}")

            return go.Pie(
                labels=labels,
                values=values,
                marker_colors=self.colors,
                hole=0.3,
                textinfo="label+percent",
                insidetextorientation="radial",
                name=title,
            )

        except Exception as e:
            logger.error(f"Error in create_pie_chart for {title}: {str(e)}")
            logger.error(f"DataFrame content: {df.to_string()}")
            raise

    def create_machine_usage_chart(
        self,
        period: str,
        avg_df: pd.DataFrame,
        best_df: pd.DataFrame,
        worst_df: pd.DataFrame,
    ) -> go.Figure:
        """
        Create a main chart with 3 pie charts side by side for a specific period.

        Args:
            period: The period for which to create the chart
            avg_df: DataFrame containing average machine data
            best_df: DataFrame containing best machine data
            worst_df: DataFrame containing worst machine data

        Returns:
            plotly.graph_objects.Figure: The combined chart figure
        """
        try:
            # Log input data for debugging
            logger.debug(f"Creating machine usage chart for period: {period}")
            logger.debug(f"Average DataFrame shape: {avg_df.shape}")
            logger.debug(f"Best DataFrame shape: {best_df.shape}")
            logger.debug(f"Worst DataFrame shape: {worst_df.shape}")

            # Create subplots with 1 row and 3 columns
            fig = make_subplots(
                rows=1,
                cols=3,
                specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
                subplot_titles=("Average Machine", "Best Machine", "Worst Machine"),
            )

            # Add pie charts to subplots
            fig.add_trace(self.create_pie_chart(avg_df, "Average"), row=1, col=1)
            fig.add_trace(self.create_pie_chart(best_df, "Best"), row=1, col=2)
            fig.add_trace(self.create_pie_chart(worst_df, "Worst"), row=1, col=3)

            # Update layout
            fig.update_layout(
                title=f"Machine Usage Distribution - {period}",
                title_x=0.5,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                margin=dict(t=100, b=0, l=0, r=0),
                height=500,
                width=1200,
            )

            return fig

        except Exception as e:
            logger.error(
                f"Error creating machine usage chart for period {period}: {str(e)}"
            )
            raise

    def get_all_periods(self) -> List[str]:
        """
        Get list of all available periods in the data.

        Returns:
            List[str]: List of period strings
        """
        machine_usage_dfs = self.dfs.get("machine_usage", {})
        return list(machine_usage_dfs.keys())


# Example usage
if __name__ == "__main__":
    from database_connection import db
    import yaml

    try:
        # Get data from database
        conn = db.connect()
        dfs = {}
        chartname = "machine_usage"
        dfs_period = {}
        file = f"1_{chartname}.sql"
        file_name = file.split(".")[0]

        # Load replace yml
        with open(f"sql/{file_name}_replace.yml", "r", encoding="utf-8") as f:
            replace_dict = yaml.safe_load(f)

        # Replace period_replace in sql file
        with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
            sql_commands = sql_file.read()

        # Create chart factory
        chart_factory = MachineUsageChart(dfs)

        # Create charts directory if it doesn't exist
        os.makedirs("charts", exist_ok=True)

        # Process each period
        for period in replace_dict["period_replace"]:
            Q = sql_commands.format(period_replace=period)
            df = db.execute_query(Q)

            # Log the raw data for debugging
            logger.debug(f"Raw data for period {period}:")
            logger.debug(df.to_string())

            # Get average, best, and worst machine data
            avg = df[df["order_index"] == 0]
            best = (
                df[df["order_index"] == 1]
                .sort_values(by="run", ascending=False)
                .iloc[0:1]
            )
            worst = (
                df[df["order_index"] == 1]
                .sort_values(by="run", ascending=True)
                .iloc[0:1]
            )

            # Log the processed data for debugging
            logger.debug(f"Average data: {avg.to_string()}")
            logger.debug(f"Best data: {best.to_string()}")
            logger.debug(f"Worst data: {worst.to_string()}")

            # Create the main chart
            fig = chart_factory.create_machine_usage_chart(period, avg, best, worst)

            # Save the chart
            fig.write_html(f"charts/machine_usage_{period}.html")
            logger.info(f"Created chart for period: {period}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        if conn:
            db.close(conn)
