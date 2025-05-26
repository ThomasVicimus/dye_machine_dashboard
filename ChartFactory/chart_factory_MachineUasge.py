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
            # * font color #fdfefe
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
                        # size="auto",
                        family="Arial, sans-serif",
                        color="#fdfefe",
                    ),
                ),
                # textfont=dict(size="auto", family="Arial, sans-serif", color="#ffffff"),
                # hoverlabel=dict(font=dict(size="auto", family="Arial, sans-serif")),
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
        plot_height: int = None,
        plot_width: int = None,
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

            plot_height: Height of the plot in pixels (default: None for auto-sizing)
            plot_width: Width of the plot in pixels (default: None for auto-sizing)
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
                    f"{period}-{lang_option[self.lang]['subplot_title'][0]}",
                    f"{period}-{lang_option[self.lang]['subplot_title'][1]}",
                    f"{period}-{lang_option[self.lang]['subplot_title'][2]}",
                ),
            )

            # Add pie charts to subplots with titles and subtitles
            fig.add_trace(
                self.create_pie_chart(
                    avg_df,
                    # f"{lang_option[self.lang]['subplot_title'][0]}",
                    # f"{period}-{lang_option[self.lang]['subplot_title'][0]}",
                    "",
                    "",
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                self.create_pie_chart(
                    best_df,
                    # f"{lang_option[self.lang]['subplot_title'][1]}",
                    # f"{period}-{best_df['machine_name'].iloc[0] if 'machine_name' in best_df.columns else lang_option[self.lang]['subplot_title'][1]}",
                    "",
                    "",
                ),
                row=1,
                col=2,
            )
            fig.add_trace(
                self.create_pie_chart(
                    worst_df,
                    # f"{lang_option[self.lang]['subplot_title'][2]}",
                    # f"{period}-{worst_df['machine_name'].iloc[0] if 'machine_name' in worst_df.columns else lang_option[self.lang]['subplot_title'][2]}",
                    "",
                    "",
                ),
                row=1,
                col=3,
            )

            # Update layout
            fig.update_layout(
                title=f"{lang_option[self.lang]['main_title']} - {period}",
                title_x=0.5,
                # title_font=dict(size=title_font_size),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="right",
                    x=1,
                    # font=dict(size=legend_font_size),
                ),
                # height=plot_height,
                # width=plot_width,
                autosize=True,
                # * Transparent background
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#fdfefe"),
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
        plot_height: int = None,
        plot_width: int = None,
        title_font_size: int = 14,
        legend_font_size: int = 9,
        margin_top: int = 30,
        margin_bottom: int = 30,
        margin_left: int = 10,
        margin_right: int = 10,
    ) -> go.Figure:
        """
        Create a simplified chart for mobile view showing only average data.

        Args:
            period: The period for which to create the chart
            dfs: Dictionary containing dataframes for different charts
            plot_height: Height of the plot in pixels (default: None for auto-sizing)
            plot_width: Width of the plot in pixels (default: None for auto-sizing)
            title_font_size: Font size for the title (default: 14)
            legend_font_size: Font size for legend text (default: 9)
            margin_top: Top margin in pixels (default: 30)
            margin_bottom: Bottom margin in pixels (default: 30)
            margin_left: Left margin in pixels (default: 10)
            margin_right: Right margin in pixels (default: 10)

        Returns:
            plotly.graph_objects.Figure: The mobile chart figure
        """
        try:
            avg_df = dfs[period]["avg"]
            # Create figure
            fig = go.Figure()

            # Add pie chart
            fig.add_trace(
                self.create_pie_chart(
                    avg_df,
                    f"{lang_option[self.lang]['subplot_title'][0]}",
                    f"{period}",
                )
            )

            # Update layout
            fig.update_layout(
                title=f"{lang_option[self.lang]['main_title']}",
                title_x=0.5,
                title_font=dict(size=title_font_size),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
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
                autosize=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#fdfefe"),
            )

            return fig

        except Exception as e:
            logger.error(f"Error in create_machine_usage_chart_mobile: {str(e)}")
            # Create empty figure with error message
            fig = go.Figure()
            fig.update_layout(
                title="Error Loading Chart",
                annotations=[
                    dict(
                        text=f"Error: {str(e)}",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        x=0.5,
                        y=0.5,
                    )
                ],
                autosize=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#fdfefe"),
            )
            return fig

    def create_machine_usage_chart_mobile_all_machine(
        self,
        period: str,
        dfs: Dict[str, Dict[str, pd.DataFrame]],
        plot_height: int = None,
        plot_width: int = None,
        title_font_size: int = 14,
        subplot_title_font_size: int = 12,
        legend_font_size: int = 9,
        margin_top: int = 25,
        margin_bottom: int = 25,
        margin_left: int = 10,
        margin_right: int = 10,
    ) -> List[go.Figure]:
        """
        Create detailed charts for each machine in the dataset for mobile detail view.

        Args:
            period: The period for which to create the chart
            dfs: Dictionary containing dataframes for all machines
            plot_height: Height of the plot in pixels (default: None for auto-sizing)
            plot_width: Width of the plot in pixels (default: None for auto-sizing)
            title_font_size: Font size for the main title (default: 14)
            subplot_title_font_size: Font size for subplot titles (default: 12)
            legend_font_size: Font size for legend text (default: 9)
            margin_top: Top margin in pixels (default: 40)
            margin_bottom: Bottom margin in pixels (default: 40)
            margin_left: Left margin in pixels (default: 10)
            margin_right: Right margin in pixels (default: 10)

        Returns:
            List[plotly.graph_objects.Figure]: List of figures for each machine
        """
        try:
            figures = []

            # First figure: Avg, Best, Worst
            if all(key in dfs[period] for key in ["avg", "best", "worst"]):
                avg_df = dfs[period]["avg"]
                best_df = dfs[period]["best"]
                worst_df = dfs[period]["worst"]

                # Create first figure with avg, best, worst
                subplot_titles = [
                    f"{lang_option[self.lang]['subplot_title'][0]}",  # Average
                    f"{lang_option[self.lang]['subplot_title'][1]}",  # Best
                    f"{lang_option[self.lang]['subplot_title'][2]}",  # Worst
                ]

                fig = make_subplots(
                    rows=1,
                    cols=3,
                    specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
                    subplot_titles=subplot_titles,
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

                # Update layout for the first figure
                fig.update_layout(
                    title="",
                    # f"{lang_option[self.lang]['main_title']} - {period} (Summary)",
                    title_x=0.5,
                    title_font=dict(size=title_font_size),
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.1,
                        xanchor="center",
                        x=0.5,
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
                    autosize=True,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#fdfefe"),
                )
                # Update subplot title fonts
                fig.update_annotations(
                    font=dict(
                        size=subplot_title_font_size,
                        family="Arial, sans-serif",
                        color="#fdfefe",
                    )
                )

                figures.append(fig)

            # Check if all_machine data exists
            if "all_machine" not in dfs[period] or dfs[period]["all_machine"].empty:
                logger.warning(
                    f"'all_machine' data not found or empty for period {period}."
                )
                return figures  # Return figures with just the first summary chart if available

            all_machine_df = dfs[period]["all_machine"]

            if "machine_name" not in all_machine_df.columns:
                logger.warning(
                    "'machine_name' column missing in 'all_machine' DataFrame. Using generic names."
                )
                all_machine_df["machine_name"] = [
                    f"Machine {i+1}" for i in range(len(all_machine_df))
                ]

            logger.debug(f"Creating individual machine charts for period: {period}")
            logger.debug(f"All Machines DataFrame shape: {all_machine_df.shape}")

            num_machines = len(all_machine_df)
            machines_per_figure = 3

            # Calculate number of figures needed for individual machines
            # Each figure will have exactly 3 charts (machines per figure)
            num_additional_figures = math.ceil(num_machines / machines_per_figure)

            # Process each figure
            for i in range(num_additional_figures):
                start_idx = i * machines_per_figure
                end_idx = min((i + 1) * machines_per_figure, num_machines)
                current_machines_df = all_machine_df.iloc[start_idx:end_idx]
                num_machines_in_fig = len(current_machines_df)

                # Calculate how many placeholder charts are needed
                num_placeholders = 0
                if num_machines_in_fig < machines_per_figure:
                    num_placeholders = machines_per_figure - num_machines_in_fig

                # Get machine names for subplot titles
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

                # Add placeholder titles if needed
                for p in range(num_placeholders):
                    subplot_titles.append("")  # Empty title for placeholder

                # Always create with exactly 3 columns
                fig = make_subplots(
                    rows=1,
                    cols=machines_per_figure,
                    specs=[[{"type": "pie"}] * machines_per_figure],
                    subplot_titles=subplot_titles,
                )

                # Add machine pie charts
                for j in range(num_machines_in_fig):
                    machine_data = current_machines_df.iloc[[j]]  # Pass as DataFrame
                    machine_name = subplot_titles[j]  # Use the already determined title

                    pie_trace = self.create_pie_chart(
                        machine_data,
                        title=f"{period} - {machine_name}",  # Main title for the pie (used as name)
                        subtitle=machine_name,  # Subtitle for the pie
                    )
                    # Remove the individual title generated by create_pie_chart as we use subplot_titles
                    pie_trace.title = None

                    fig.add_trace(
                        pie_trace,
                        row=1,
                        col=j + 1,
                    )

                # Add placeholder empty pie charts if needed
                # These ensure every figure has exactly 3 charts for visual consistency
                for p in range(num_placeholders):
                    j = num_machines_in_fig + p
                    # Create an empty/placeholder pie chart
                    empty_data = pd.DataFrame(
                        {"run": [0], "idle": [0], "down": [0], "repair": [0]}
                    )

                    # Use transparent colors for placeholder
                    empty_pie = go.Pie(
                        labels=lang_option[self.lang]["legend"],
                        values=[0, 0, 0, 0],  # Zero values
                        marker_colors=["rgba(0,0,0,0)"] * 4,  # Transparent colors
                        showlegend=False,
                        textinfo="none",
                        hoverinfo="none",
                        name="",
                    )

                    fig.add_trace(
                        empty_pie,
                        row=1,
                        col=j + 1,
                    )

                # Update layout for the current figure
                fig.update_layout(
                    title="",
                    # f"{lang_option[self.lang]['main_title']} - {period} ({lang_option[self.lang]['machine']} {start_idx+1}-{end_idx})",
                    title_x=0.5,
                    title_font=dict(size=title_font_size),
                    showlegend=False,
                    # showlegend=(
                    #     True if i == 0 else False
                    # ),  # Show legend only on first machine figure
                    # legend=dict(
                    #     orientation="h",
                    #     yanchor="bottom",
                    #     y=-0.1,  # Adjust legend position
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
                    autosize=True,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#fdfefe"),
                )

                # Update subplot title fonts
                fig.update_annotations(
                    font=dict(
                        size=subplot_title_font_size,
                        family="Arial, sans-serif",
                    )
                )

                figures.append(fig)

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


# # Example usage
# if __name__ == "__main__":
#     from database_connection import db
#     import yaml

#     try:
#         # Get data from database
#         conn = db.connect()
#         dfs = {}
#         chartname = "machine_usage"
#         chart_factory = MachineUsageChart(dfs, lang="zh_cn")  # Change language here
#         dfs = get_MachineUsage_data(db)

#         for period in dfs.keys():
#             # Create the main chart
#             fig = chart_factory.create_machine_usage_chart(period, dfs)

#             # Save the chart
#             fig.write_html(f"charts/machine_usage_{period}.html")
#             logger.info(f"Created chart for period: {period}")

#     except Exception as e:
#         logger.error(f"Error in main execution: {str(e)}")
#     finally:
#         if conn:
#             db.close(conn)
