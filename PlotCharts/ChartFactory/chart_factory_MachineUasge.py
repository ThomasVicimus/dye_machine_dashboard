import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List
import logging
import yaml
import math

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

    def create_machine_usage_chart_mobile_main(
        self,
        period: str,
        dfs: Dict[str, Dict[str, pd.DataFrame]],
        plot_height: int = 230,
        plot_width: int = 250,
        title_font_size: int = 14,
        legend_font_size: int = 9,
        margin_top: int = 50,
        margin_bottom: int = 50,
        margin_left: int = 10,
        margin_right: int = 10,
    ) -> go.Figure:
        """
        Create a single pie chart for the average machine usage, suitable for mobile view.

        Args:
            period: The period for the chart.
            avg_df: DataFrame containing the average machine usage data.
            plot_height: Height of the plot in pixels (default: 300)
            plot_width: Width of the plot in pixels (default: 300)
            title_font_size: Font size for the main title (default: 14)
            legend_font_size: Font size for legend text (default: 9)
            margin_top: Top margin in pixels (default: 50)
            margin_bottom: Bottom margin in pixels (default: 50)
            margin_left: Left margin in pixels (default: 10)
            margin_right: Right margin in pixels (default: 10)

        Returns:
            plotly.graph_objects.Figure: The pie chart figure.
        """
        try:
            avg_df = dfs[period]["avg"]
            logger.debug(f"Creating mobile main chart for period: {period}")
            logger.debug(f"Input Average DataFrame shape: {avg_df.shape}")

            fig = go.Figure()

            pie_trace = self.create_pie_chart(
                avg_df,
                title="",  # Title handled by layout
                subtitle=f"{lang_option[self.lang]['subplot_title'][0]}",  # Use 'Average' as subtitle directly on pie
            )
            # Remove individual pie title as we have main layout title
            pie_trace.title = None
            fig.add_trace(pie_trace)

            # Update layout for a single chart, mobile-friendly
            fig.update_layout(
                title=f"{lang_option[self.lang]['main_title']} - {period} ({lang_option[self.lang]['subplot_title'][0]})",
                title_x=0.5,
                title_font=dict(size=title_font_size),
                showlegend=True,
                # legend=dict(
                #     orientation="v",
                #     yanchor="bottom",
                #     y=-0.15,  # Adjust legend position slightly
                #     xanchor="center",
                #     x=0.5,
                #     font=dict(size=legend_font_size),
                # ),
                margin=dict(
                    t=margin_top,
                    b=margin_bottom,
                    l=margin_left,
                    r=margin_right,
                ),
                height=plot_height,
                width=plot_width,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    # Remove subplot annotations if they exist (shouldn't for single chart)
                ],
            )

            return fig

        except Exception as e:
            logger.error(
                f"Error creating mobile machine usage chart for period {period}: {str(e)}"
            )
            raise

    def create_machine_usage_chart_mobile_all_machine(
        self,
        period: str,
        dfs: Dict[str, Dict[str, pd.DataFrame]],
        plot_height: int = 230,
        plot_width: int = 250,
        title_font_size: int = 14,
        subplot_title_font_size: int = 12,
        legend_font_size: int = 9,
        margin_top: int = 50,
        margin_bottom: int = 50,
        margin_left: int = 10,
        margin_right: int = 10,
    ) -> List[go.Figure]:
        """
        Creates a list of figures, each containing up to 3 pie charts
        representing individual machine usage from the 'all_machine' data.

        Args:
            period: The period for which to create the charts.
            dfs: Dictionary containing dataframes for different charts,
                 including 'all_machine'.
            plot_height: Height of each plot in pixels (default: 400).
            plot_width: Width of each plot in pixels (default: 600).
            title_font_size: Font size for the main title (default: 16).
            subplot_title_font_size: Font size for subplot titles (default: 14).
            legend_font_size: Font size for legend text (default: 10).
            margin_top: Top margin in pixels (default: 70).
            margin_bottom: Bottom margin in pixels (default: 60).
            margin_left: Left margin in pixels (default: 20).
            margin_right: Right margin in pixels (default: 20).

        Returns:
            List[plotly.graph_objects.Figure]: A list of figure objects.
        """
        try:
            if period not in dfs or "all_machine" not in dfs[period]:
                logger.warning(
                    f"'all_machine' data not found for period {period}. Skipping chart creation."
                )
                return []

            all_machine_df = dfs[period]["all_machine"]

            if all_machine_df.empty:
                logger.info(
                    f"'all_machine' DataFrame is empty for period {period}. No charts to create."
                )
                return []

            if "machine_name" not in all_machine_df.columns:
                logger.error(
                    "'machine_name' column missing in 'all_machine' DataFrame."
                )
                # Handle missing column, e.g., assign default names or raise error
                # For now, create generic names
                all_machine_df["machine_name"] = [
                    f"Machine {i+1}" for i in range(len(all_machine_df))
                ]
                # raise ValueError("'machine_name' column missing in 'all_machine' DataFrame.")

            logger.debug(f"Creating individual machine charts for period: {period}")
            logger.debug(f"All Machines DataFrame shape: {all_machine_df.shape}")

            num_machines = len(all_machine_df)
            charts_per_figure = 3
            num_figures = math.ceil(num_machines / charts_per_figure)
            figures = []

            # Use a consistent legend across all figures based on the first figure's traces
            show_legend_for_figure = True

            for i in range(num_figures):
                start_idx = i * charts_per_figure
                end_idx = min((i + 1) * charts_per_figure, num_machines)
                current_machines_df = all_machine_df.iloc[start_idx:end_idx]
                num_cols = len(current_machines_df)

                if num_cols == 0:
                    continue

                # Get machine names for subplot titles, handle potential missing names
                subplot_titles = [
                    (
                        str(name)
                        if pd.notna(name)
                        else f"{lang_option[self.lang]['machine']} {idx+1}"
                    )
                    for idx, name in enumerate(
                        current_machines_df["machine_name"], start=start_idx
                    )
                ]

                fig = make_subplots(
                    rows=1,
                    cols=num_cols,
                    specs=[[{"type": "pie"}] * num_cols],
                    subplot_titles=subplot_titles,
                )

                for j in range(num_cols):
                    machine_data = current_machines_df.iloc[[j]]  # Pass as DataFrame
                    machine_name = subplot_titles[j]  # Use the already determined title

                    pie_trace = self.create_pie_chart(
                        machine_data,
                        title=machine_name,  # Main title for the pie (used as name)
                        subtitle=machine_name,  # Subtitle for the pie
                    )
                    # Remove the individual title generated by create_pie_chart as we use subplot_titles
                    pie_trace.title = None

                    fig.add_trace(
                        pie_trace,
                        row=1,
                        col=j + 1,
                    )

                # Update layout for the current figure
                fig.update_layout(
                    title=f"{lang_option[self.lang]['main_title']} - {period} ({lang_option[self.lang]['machine']} {start_idx+1}-{end_idx})",
                    title_x=0.5,
                    title_font=dict(size=title_font_size),
                    showlegend=show_legend_for_figure,  # Show legend only needed once
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.1,  # Adjust legend position
                        xanchor="center",
                        x=0.5,
                        font=dict(size=legend_font_size),
                        # Use labels from the first trace for consistency if needed
                        # traceorder='reversed',
                        # title_text='Status'
                    ),
                    margin=dict(
                        t=margin_top,
                        b=margin_bottom,
                        l=margin_left,
                        r=margin_right,
                    ),
                    height=plot_height,
                    width=plot_width,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )

                # Update subplot title fonts
                fig.update_annotations(
                    font=dict(
                        size=subplot_title_font_size,
                        family="Arial, sans-serif",
                    )
                )

                figures.append(fig)
                # After the first figure, we can potentially hide the legend if redundant
                # show_legend_for_figure = False # Uncomment if you want legend only on the first figure

            return figures

        except Exception as e:
            logger.error(
                f"Error creating all machines charts for period {period}: {str(e)}"
            )
            # Log the DataFrame that caused the error
            if "all_machine_df" in locals():
                logger.error(
                    f"Problematic DataFrame content:\n{all_machine_df.to_string()}"
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
            avg = get_avg_chart1(df)
            # print(f"avg: {avg}")
        else:
            avg = df[df["order_index"] == 0]

        best = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=False).iloc[0:1]
        )
        worst = (
            df[df["order_index"] == 1].sort_values(by="run", ascending=True).iloc[0:1]
        )
        all_machine = df[df["order_index"] == 1].sort_values(by="run", ascending=True)
        dfs[period] = {
            "avg": avg,
            "best": best,
            "worst": worst,
            "all_machine": all_machine,
        }

    return dfs


def get_avg_chart1(df):
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
