import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Language options for titles
lang_option = {
    "en": {
        "main_title": "Machine Usage",
        "subplot_title": ["Average", "Best", "Worst"],
        "usage": "Usage %",
        "machine": "Machine",
        "legend": ["Running", "Idle", "Down", "Repair"],
    },
    "zh_hk": {
        "main_title": "設備使用率",
        "subplot_title": ["平均", "最佳", "最差"],
        "usage": "使用率 %",
        "machine": "設備",
        "legend": ["運行", "閒置", "停機", "維修"],
    },
    "zh_cn": {
        "main_title": "设备使用率",
        "subplot_title": ["平均", "最佳", "最差"],
        "usage": "使用率 %",
        "machine": "设备",
        "legend": ["运行", "闲置", "停机", "维修"],
    },
}


class MachineUsageChart:
    def __init__(self, dfs: Dict[str, Dict[str, pd.DataFrame]], lang: str = "en"):
        """
        Initialize the chart factory with the dataframes containing machine usage data.

        Args:
            dfs: Dictionary containing dataframes for different charts
            lang: Language option ('en', 'zh_hk', 'zh_cn')
        """
        self.dfs = dfs
        self.lang = lang if lang in lang_option else "en"
        self.colors = [
            "#2ecc71",
            "#f1c40f",
            "#e74c3c",
            "#3498db",
        ]  # Green, Yellow, Red, Blue

    def create_pie_chart(self, df: pd.DataFrame, title: str, subtitle: str) -> go.Pie:
        """
        Create a single pie chart trace.

        Args:
            df: DataFrame containing the data
            title: Title for the pie chart
            subtitle: Subtitle for the pie chart

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
            labels = lang_option[self.lang]["legend"]

            # Log the values being used
            logger.debug(f"Values for pie chart: {values}")
            logger.debug(f"Type of values: {type(values)}")

            return go.Pie(
                labels=labels,
                values=values,
                marker_colors=self.colors,
                hole=0.3,
                textinfo="percent",
                textposition="inside",
                insidetextorientation="radial",
                name=title,
                title=dict(
                    # text=f"{title}<br><br><sup>{subtitle}</sup>",  # Added extra <br> for spacing
                    text=f"{subtitle}<br><br>",  # Added extra <br> for spacing
                    position="top center",
                    font=dict(
                        size=16, family="Arial, sans-serif"  # Increased title font size
                    ),
                ),
            )

        except Exception as e:
            logger.error(f"Error in create_pie_chart for {title}: {str(e)}")
            logger.error(f"DataFrame content: {df.to_string()}")
            raise

    def create_machine_usage_chart(
        self,
        period: str,
        dfs: Dict[str, Dict[str, pd.DataFrame]],
        # avg_df: pd.DataFrame,
        # best_df: pd.DataFrame,
        # worst_df: pd.DataFrame,
        plot_height: int = 400,
        plot_width: int = 500,
        title_font_size: int = 16,
        subplot_title_font_size: int = 14,
        legend_font_size: int = 10,
        margin_top: int = 60,
        margin_bottom: int = 60,
        margin_left: int = 20,
        margin_right: int = 20,
    ) -> go.Figure:
        """
        Create a main chart with 3 pie charts side by side for a specific period.

        Args:
            period: The period for which to create the chart
            dfs: Dictionary containing dataframes for different charts

            plot_height: Height of the plot in pixels (default: 400)
            plot_width: Width of the plot in pixels (default: 500)
            title_font_size: Font size for the main title (default: 16)
            subplot_title_font_size: Font size for subplot titles (default: 14)
            legend_font_size: Font size for legend text (default: 10)
            margin_top: Top margin in pixels (default: 60)
            margin_bottom: Bottom margin in pixels (default: 60)
            margin_left: Left margin in pixels (default: 20)
            margin_right: Right margin in pixels (default: 20)

        Returns:
            plotly.graph_objects.Figure: The combined chart figure
        """
        try:
            avg_df = dfs[period]["avg"]
            best_df = dfs[period]["best"]
            worst_df = dfs[period]["worst"]
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
                subplot_titles=(
                    f"{lang_option[self.lang]['subplot_title'][0]}",
                    f"{lang_option[self.lang]['subplot_title'][1]}",
                    f"{lang_option[self.lang]['subplot_title'][2]}",
                ),
            )

            # Add pie charts to subplots with titles and subtitles
            fig.add_trace(
                self.create_pie_chart(
                    avg_df,
                    f"{lang_option[self.lang]['subplot_title'][0]}",
                    f"{period}-{lang_option[self.lang]['subplot_title'][0]}",
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                self.create_pie_chart(
                    best_df,
                    f"{lang_option[self.lang]['subplot_title'][1]}",
                    f"{period}-{best_df['machine_name'].iloc[0] if 'machine_name' in best_df.columns else lang_option[self.lang]['subplot_title'][1]}",
                ),
                row=1,
                col=2,
            )
            fig.add_trace(
                self.create_pie_chart(
                    worst_df,
                    f"{lang_option[self.lang]['subplot_title'][2]}",
                    f"{period}-{worst_df['machine_name'].iloc[0] if 'machine_name' in worst_df.columns else lang_option[self.lang]['subplot_title'][2]}",
                ),
                row=1,
                col=3,
            )

            # Update layout
            fig.update_layout(
                title=f"{lang_option[self.lang]['main_title']} - {period}",
                title_x=0.5,
                title_font=dict(size=title_font_size),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="right",
                    x=1,
                    font=dict(size=legend_font_size),
                ),
                margin=dict(
                    t=margin_top,
                    b=margin_bottom,
                    l=margin_left,
                    r=margin_right,
                ),
                height=plot_height,
                width=plot_width,
                # * Transparent background
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )

            # Update subplot titles
            fig.update_annotations(
                font=dict(
                    size=subplot_title_font_size,
                    family="Arial, sans-serif",
                )
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


def get_MachineUsage_data(db) -> pd.DataFrame:
    from database_connection import db

    """
    Get machine usage data from the database.

    Returns:
        pd.DataFrame: DataFrame containing machine usage data
    """

    dfs = {}
    # load chart 1 sql
    chartname = "machine_usage"
    dfs_machine_usage = {}
    file = f"1_{chartname}.sql"
    file_name = file.split(".")[0]
    # load replace yml using unicodedecode
    with open(f"sql/{file_name}_replace.yml", "r", encoding="utf-8") as f:
        replace_dict = yaml.safe_load(f)
    # replace period_replace in sql file
    with open(f"sql/{file}", "r", encoding="utf-8") as sql_file:
        sql_commands = sql_file.read()
    # for period in replace_dict["period_replace"]:
    #     Q = sql_commands.format(period_replace=period)
    #     dfs_machine_usage[period] = db.execute_query(Q)

    # Process each period
    for period in replace_dict["period_replace"]:
        Q = sql_commands.format(period_replace=period)
        df = db.execute_query(Q)

        # Log the raw data for debugging
        logger.debug(f"Raw data for period {period}:")
        logger.debug(df.to_string())

        # Get average, best, and worst machine data
        if not 0 in df["order_index"].unique():
            avg = get_avg(df)
            # print(f"avg: {avg}")
        else:
            avg = df[df["order_index"] == 0]

        best = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=False).iloc[0:1]
        )
        worst = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=True).iloc[0:1]
        )
        dfs[period] = {"avg": avg, "best": best, "worst": worst}

    return dfs


def get_avg(df):
    # * calculate the average of each cols in the df in form of df
    mask = df["order_index"] == 1
    _df = df[mask]
    df_avg = pd.DataFrame(
        columns=["run", "idle", "down", "repair", "period", "machine_name"]
    )
    df_avg.loc[0, "run"] = _df["run"].mean()
    df_avg.loc[0, "idle"] = _df["idle"].mean()
    df_avg.loc[0, "down"] = _df["down"].mean()
    df_avg.loc[0, "repair"] = _df["repair"].mean()
    df_avg.loc[0, "period"] = df["period"].iloc[0]
    df_avg.loc[0, "machine_name"] = pd.NA
    return df_avg


# Example usage
if __name__ == "__main__":
    from database_connection import db
    import yaml

    try:
        # Get data from database
        conn = db.connect()
        dfs = {}
        chartname = "machine_usage"
        chart_factory = MachineUsageChart(dfs, lang="zh_cn")  # Change language here
        dfs = get_MachineUsage_data(db)

        for period in dfs.keys():
            # Create the main chart
            fig = chart_factory.create_machine_usage_chart(period, dfs)

            # Save the chart
            fig.write_html(f"charts/machine_usage_{period}.html")
            logger.info(f"Created chart for period: {period}")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
    finally:
        if conn:
            db.close(conn)
