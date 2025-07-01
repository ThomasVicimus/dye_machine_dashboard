import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Language options for titles and labels
lang_option_chart4 = {
    "en": {
        "main_title": "Machine Resource Consumption",
        "subplot_title": ["Average", "Best", "Worst"],
        "metrics": ["Steam (ton)", "Power (kWh)", "Water (ton)"],
        # "y_axis_title": "Consumption",
        # "machine_prefix": "Machine",
    },
    "zh_hk": {
        "main_title": "能耗/KG",
        "subplot_title": ["平均", "最佳", "最差"],
        "metrics": ["蒸汽量 (噸)", "用電量 (kWh)", "用水量 (噸)"],
        # "y_axis_title": "消耗量",
        # "machine_prefix": "設備",
    },
    "zh_cn": {
        "main_title": "能耗/KG",
        "subplot_title": ["平均", "最佳", "最差"],
        "metrics": ["汽", "电", "水"],
        # "y_axis_title": "消耗量",
        # "machine_prefix": "设备",
    },
}


def _add_bar_traces_for_category_subplot(
    fig: go.Figure,
    df: pd.DataFrame,
    lang: str,
    row_num: int,
    col_num: int,
    add_to_legend: bool,
    category_name_for_log: str,
):
    """
    Adds a group of bar traces (water, power, steam) for a single category (Avg, Best, Worst)
    to a specified subplot in the figure.
    """
    current_lang_opts = lang_option_chart4.get(lang, lang_option_chart4["zh_cn"])
    metrics_db_keys = ["steam_ton", "power_kwh", "water_ton"]
    metric_display_names = current_lang_opts["metrics"]
    # Distinct colors for each metric, consistent with other charts if possible
    metric_colors = [
        "#f1c40f",
        "#3498db",
        "#2ecc71",
    ]  # Yellow (Steam), Blue (Power), Green (Water)

    values = [0.0] * len(metrics_db_keys)  # Default to zeros

    if (
        df is None
        or df.empty
        or not all(col in df.columns for col in metrics_db_keys)
        or len(df) == 0
    ):
        logger.warning(
            f"DataFrame for '{category_name_for_log}' is None, empty, missing required columns, or has no rows. Plotting zeros."
        )
        if df is not None and not df.empty:
            logger.debug(f"Problematic DataFrame columns: {df.columns.tolist()}")
        elif df is None:
            logger.debug("DataFrame was None.")
        else:
            logger.debug("DataFrame was empty or had no rows.")

    else:
        processed_values = []
        for key in metrics_db_keys:
            try:
                # Ensure the value is scalar and numeric
                raw_value = df[key].iloc[0]
                val = pd.to_numeric(raw_value, errors="coerce")
                processed_values.append(val if pd.notna(val) else 0.0)
            except IndexError:
                logger.error(
                    f"IndexError accessing {key} for {category_name_for_log}. DF has {len(df)} rows."
                )
                processed_values.append(0.0)
            except Exception as e:
                logger.error(
                    f"Error processing value for {key} in {category_name_for_log}: {e}"
                )
                processed_values.append(0.0)
        values = processed_values

    for i in range(len(metrics_db_keys)):
        fig.add_trace(
            go.Bar(
                x=[metric_display_names[i]],  # X-axis category for this specific bar
                y=[values[i]],
                name=metric_display_names[
                    i
                ],  # Name for the legend (Water, Power, Steam)
                marker_color=metric_colors[i],
                legendgroup="metrics",  # Groups all metric bars for a unified legend
                showlegend=add_to_legend,  # Controlled by the main function call
                text=[f"{values[i]:.2f}"],  # Display value on bar
                textposition="auto",
                hoverinfo="y+name",  # Show y-value and trace name (e.g., "Water (ton)") on hover
            ),
            row=row_num,
            col=col_num,
        )


def create_chart4_figure(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    lang: str = "zh_cn",
    margin_top: int = 60,
    margin_bottom: int = 60,
    margin_left: int = 40,
    margin_right: int = 40,
) -> go.Figure:
    """
    Creates a figure with three subplots (Average, Best, Worst resource consumption)
    as bar charts, showing water, power, and steam usage.
    """
    current_lang_opts = lang_option_chart4.get(lang, lang_option_chart4["zh_cn"])

    # Basic error figure setup
    def _create_error_figure(message: str) -> go.Figure:
        fig_error = go.Figure()
        fig_error.update_layout(
            title_text=message,
            title_x=0.5,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            xaxis_visible=False,
            yaxis_visible=False,
            autosize=True,
        )
        fig_error.add_annotation(
            text="Please check data availability or report the issue.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.4,
            showarrow=False,
            font=dict(size=12, color="#fdfefe"),
        )
        return fig_error

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs.get(period), dict)
            or not all(key in dfs.get(period, {}) for key in ["avg", "best", "worst"])
        ):
            logger.error(
                f"Data for period '{period}' is missing required keys ('avg', 'best', 'worst') or not structured correctly for chart4."
            )
            return _create_error_figure(
                f"Data Error for Chart4: {period} - Invalid Structure"
            )

        data_for_period = dfs[period]
        avg_df = data_for_period.get("avg")
        best_df = data_for_period.get("best")
        worst_df = data_for_period.get("worst")

        if avg_df is None or best_df is None or worst_df is None:
            logger.error(
                f"One or more dataframes (avg, best, worst) are None for period '{period}'."
            )
            return _create_error_figure(
                f"Data Error for Chart4: {period} - Missing Data"
            )

    except Exception as e:  # Catch any other unexpected error during data extraction
        logger.error(
            f"Unexpected error accessing data for chart4, period '{period}': {str(e)}"
        )
        return _create_error_figure(f"Unexpected Data Error for Chart4: {period}")

    # Calculate maximum y-value across all categories for unified y-axis scaling
    metrics_db_keys = ["steam_ton", "power_kwh", "water_ton"]
    max_y_value_overall = 0.0

    for df in [avg_df, best_df, worst_df]:
        if (
            df is not None
            and not df.empty
            and all(col in df.columns for col in metrics_db_keys)
        ):
            try:
                for key in metrics_db_keys:
                    raw_value = df[key].iloc[0]
                    val = pd.to_numeric(raw_value, errors="coerce")
                    if pd.notna(val):
                        max_y_value_overall = max(max_y_value_overall, val)
            except (IndexError, Exception) as e:
                logger.debug(f"Error processing values for y-axis scaling: {e}")
                continue

    # Add 10% padding to the maximum value for better visualization
    if max_y_value_overall > 0:
        max_y_value_overall *= 1.1
    else:
        max_y_value_overall = 1.0  # Default minimum range if no valid data

    # Construct subplot titles, adding machine names if available
    subplot_titles_text = [
        f"{period} {current_lang_opts['subplot_title'][0]}",  # Average
        f"{period} {current_lang_opts['subplot_title'][1]}",  # Best
        f"{period} {current_lang_opts['subplot_title'][2]}",  # Worst
    ]

    # Add machine name to "Best" subplot title
    if (
        best_df is not None
        and not best_df.empty
        and "machine_name" in best_df.columns
        and pd.notna(best_df["machine_name"].iloc[0])
    ):
        subplot_titles_text[1] += f" - ({best_df['machine_name'].iloc[0]}) <br><br>"
    elif (
        best_df is not None and not best_df.empty
    ):  # If machine_name is missing but df exists
        logger.debug(
            f"Best DF for {period} is missing 'machine_name' or it's NaN. Columns: {best_df.columns.tolist()}"
        )

    # Add machine name to "Worst" subplot title
    if (
        worst_df is not None
        and not worst_df.empty
        and "machine_name" in worst_df.columns
        and pd.notna(worst_df["machine_name"].iloc[0])
    ):
        subplot_titles_text[2] += f" - ({worst_df['machine_name'].iloc[0]}) <br><br>"
    elif worst_df is not None and not worst_df.empty:
        logger.debug(
            f"Worst DF for {period} is missing 'machine_name' or it's NaN. Columns: {worst_df.columns.tolist()}"
        )

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=subplot_titles_text,
        horizontal_spacing=0.08,  # Adjust spacing between subplots
    )

    # Add bar traces for each category
    # Average (col 1) - contributes to legend
    _add_bar_traces_for_category_subplot(
        fig,
        avg_df,
        lang,
        1,
        1,
        add_to_legend=True,
        category_name_for_log=subplot_titles_text[0],
    )
    # Best (col 2) - does not contribute to legend
    _add_bar_traces_for_category_subplot(
        fig,
        best_df,
        lang,
        1,
        2,
        add_to_legend=False,
        category_name_for_log=subplot_titles_text[1],
    )
    # Worst (col 3) - does not contribute to legend
    _add_bar_traces_for_category_subplot(
        fig,
        worst_df,
        lang,
        1,
        3,
        add_to_legend=False,
        category_name_for_log=subplot_titles_text[2],
    )

    main_title_text = f"{current_lang_opts['main_title']} - {period}"
    fig.update_layout(
        title_text=main_title_text,
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            bgcolor="rgba(0,0,0,0)",
        ),
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fdfefe",
        margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
    )

    # Update subplot titles appearance
    fig.update_annotations(font_family="Arial, sans-serif")

    # Style axes for all subplots with unified y-axis range
    for i in range(1, 4):  # For columns 1, 2, 3
        fig.update_xaxes(
            row=1,
            col=i,
            showline=True,
            linewidth=1,
            linecolor="#fdfefe",
            showgrid=False,
            tickfont=dict(
                color="#fdfefe", size=10
            ),  # Smaller tick font for metric names
            type="category",  # Ensures x-axis treats items as discrete categories
        )
        fig.update_yaxes(
            row=1,
            col=i,
            showline=False,
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(128,128,128,0.2)",
            tickfont=dict(color="#fdfefe"),
            range=[0, max_y_value_overall],  # Unified y-axis range
        )

    return fig


def create_chart4_figure_mobile(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    lang: str = "zh_cn",
    margin_top: int = 30,
    margin_bottom: int = 60,
    margin_left: int = 10,
    margin_right: int = 10,
) -> go.Figure:
    """
    Creates a single bar chart for average resource consumption,
    showing water, power, and steam usage, optimized for mobile view.
    """
    current_lang_opts = lang_option_chart4.get(lang, lang_option_chart4["zh_cn"])

    # Re-use or adapt error figure creation logic
    def _create_error_figure_mobile(message: str) -> go.Figure:
        fig_error = go.Figure()
        fig_error.update_layout(
            title_text=message,
            title_x=0.5,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            xaxis_visible=False,
            yaxis_visible=False,
            autosize=True,
        )
        fig_error.add_annotation(
            text="Please check data availability or report the issue.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.4,
            showarrow=False,
            font=dict(size=10, color="#fdfefe"),
        )
        return fig_error

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs.get(period), dict)
            or "avg" not in dfs.get(period, {})
        ):
            logger.error(
                f"Data for period '{period}' is missing 'avg' key or not structured correctly for chart4 mobile."
            )
            return _create_error_figure_mobile(
                f"Data Error: {period} - Invalid Structure (Mobile)"
            )

        data_for_period = dfs[period]
        avg_df = data_for_period.get("avg")

        if avg_df is None:
            logger.error(
                f"Average dataframe (avg_df) is None for period '{period}' for chart4 mobile."
            )
            return _create_error_figure_mobile(
                f"Data Error: {period} - Missing Average Data (Mobile)"
            )

    except Exception as e:
        logger.error(
            f"Unexpected error accessing data for chart4 mobile, period '{period}': {str(e)}"
        )
        return _create_error_figure_mobile(f"Unexpected Data Error: {period} (Mobile)")

    fig = make_subplots(rows=1, cols=1)

    # Add bar traces for the average category
    # Since _add_bar_traces_for_category_subplot is designed for subplots,
    # we pass row=1, col=1, but it will draw on the main fig.
    # This assumes _add_bar_traces_for_category_subplot correctly adds to a single figure
    # if it's not part of make_subplots context (which it should).
    _add_bar_traces_for_category_subplot(
        fig,
        avg_df,
        lang,
        row_num=1,  # Placeholder, not strictly used by go.Figure directly but required by helper
        col_num=1,  # Placeholder
        add_to_legend=True,
        category_name_for_log=current_lang_opts["subplot_title"][0],  # "Average"
    )

    main_title_text = f"{current_lang_opts['main_title']} - {current_lang_opts['subplot_title'][0]} - {period}"

    fig.update_layout(
        title_text=main_title_text,
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            bgcolor="rgba(0,0,0,0)",
        ),
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fdfefe",
        margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
        barmode="group",  # Ensures bars are grouped if multiple traces were on the same x category
    )

    # Style axes
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="#fdfefe",
        showgrid=False,
        tickfont=dict(color="#fdfefe", size=10),
        type="category",
    )
    fig.update_yaxes(
        title_text="",
        showline=False,
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor="rgba(128,128,128,0.2)",
        tickfont=dict(color="#fdfefe"),
        rangemode="tozero",  # Ensure y-axis starts at 0
    )

    return fig


def create_chart4_figure_detail(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    lang: str = "zh_cn",
    title_font_size: int = 16,  # Adjusted default
    subplot_title_font_size: int = 12,
    legend_font_size: int = 10,  # Adjusted default
    margin_top: int = 40,  # Adjusted default
    margin_bottom: int = 60,
    margin_left: int = 15,  # Changed from 40
    margin_right: int = 15,  # Changed from 40
    plot_width: int = None,
    row_height_px: int = 250,  # Adjusted for a bit more space per fig-row
) -> List[go.Figure]:
    """
    Creates a list of figures. Each figure represents a row of charts.
    - output_figures[0]: Summary (Average, Best, Worst) in 1x3 subplots.
    - output_figures[1...N]: Machine data, 3 machines per figure (1x3 subplots each).
    """
    output_figures: List[go.Figure] = []
    current_lang_opts = lang_option_chart4.get(lang, lang_option_chart4["zh_cn"])
    metrics_db_keys = ["steam_ton", "power_kwh", "water_ton"]
    machines_per_row_fig = 3

    # --- Error Figure Creation (returns a list with one error figure) ---
    def _create_error_figure_list(message: str) -> List[go.Figure]:
        fig_error = go.Figure()
        layout_args_error = dict(
            title_text=message,
            title_x=0.5,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            xaxis_visible=False,
            yaxis_visible=False,
            height=row_height_px,
        )
        if plot_width is not None:
            layout_args_error["width"] = plot_width
            layout_args_error["autosize"] = False
        else:
            layout_args_error["autosize"] = True
        fig_error.update_layout(**layout_args_error)
        fig_error.add_annotation(
            text="Data Error. Check logs or data source.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.4,
            showarrow=False,
            font=dict(size=12, color="#fdfefe"),
        )
        return [fig_error]

    # --- Data Preparation ---
    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs.get(period), dict)
        ):
            return _create_error_figure_list(f"Data Structure Error: {period}")
        data_for_period = dfs[period]
        avg_df = data_for_period.get("avg")
        best_df = data_for_period.get("best")
        worst_df = data_for_period.get("worst")
        all_machine_df_original = data_for_period.get("all_machine")

        if avg_df is None or best_df is None or worst_df is None:
            return _create_error_figure_list(
                f"Missing Key Data: {period} (Avg/Best/Worst)"
            )
        all_machine_df = (
            all_machine_df_original.copy()
            if all_machine_df_original is not None
            else pd.DataFrame()
        )
    except Exception as e:
        logger.error(f"Error during data prep for chart4_figure_detail: {e}")
        return _create_error_figure_list(f"Data Preparation Error: {period}")

    # --- Figure 1: Summary (Average, Best, Worst) ---
    summary_fig_height = row_height_px  # Base height for a row
    if title_font_size:
        summary_fig_height += title_font_size + 10  # Add space for main title
    if subplot_title_font_size:
        summary_fig_height += (
            subplot_title_font_size + 5
        )  # Add space for subplot titles
    if legend_font_size:
        summary_fig_height += legend_font_size + 30  # Add space for legend at bottom

    # Calculate maximum y-value across all categories for unified y-axis scaling in summary
    max_y_value_summary = 0.0

    for df in [avg_df, best_df, worst_df]:
        if (
            df is not None
            and not df.empty
            and all(col in df.columns for col in metrics_db_keys)
        ):
            try:
                for key in metrics_db_keys:
                    raw_value = df[key].iloc[0]
                    val = pd.to_numeric(raw_value, errors="coerce")
                    if pd.notna(val):
                        max_y_value_summary = max(max_y_value_summary, val)
            except (IndexError, Exception) as e:
                logger.debug(f"Error processing values for summary y-axis scaling: {e}")
                continue

    # Add 10% padding to the maximum value for better visualization
    if max_y_value_summary > 0:
        max_y_value_summary *= 1.1
    else:
        max_y_value_summary = 1.0  # Default minimum range if no valid data

    s_title_avg = f"{period} {current_lang_opts['subplot_title'][0]}"
    s_title_best = f"{period} {current_lang_opts['subplot_title'][1]}"
    s_title_worst = f"{period} {current_lang_opts['subplot_title'][2]}"
    if (
        best_df is not None
        and not best_df.empty
        and "machine_name" in best_df.columns
        and pd.notna(best_df["machine_name"].iloc[0])
    ):
        s_title_best += f" ({best_df['machine_name'].iloc[0]})"
    if (
        worst_df is not None
        and not worst_df.empty
        and "machine_name" in worst_df.columns
        and pd.notna(worst_df["machine_name"].iloc[0])
    ):
        s_title_worst += f" ({worst_df['machine_name'].iloc[0]})"

    fig_summary = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[s_title_avg, s_title_best, s_title_worst],
        horizontal_spacing=0.04,
    )
    _add_bar_traces_for_category_subplot(
        fig_summary, avg_df, lang, 1, 1, True, s_title_avg
    )
    _add_bar_traces_for_category_subplot(
        fig_summary, best_df, lang, 1, 2, False, s_title_best
    )
    _add_bar_traces_for_category_subplot(
        fig_summary, worst_df, lang, 1, 3, False, s_title_worst
    )

    summary_main_title = f"{current_lang_opts['main_title']} - {period} (Summary)"
    summary_layout_args = dict(
        title_text=summary_main_title,
        title_x=0.5,
        title_font_size=title_font_size,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font_size=legend_font_size,
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fdfefe",
        height=summary_fig_height,
        margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
    )
    if plot_width:
        summary_layout_args.update({"width": plot_width, "autosize": False})
    else:
        summary_layout_args["autosize"] = True
    fig_summary.update_layout(**summary_layout_args)
    fig_summary.update_annotations(
        font_size=subplot_title_font_size
    )  # For subplot titles
    for c_idx in range(1, 4):  # Axes for summary fig with unified y-axis scaling
        fig_summary.update_xaxes(
            row=1,
            col=c_idx,
            showline=True,
            linewidth=1,
            linecolor="#fdfefe",
            showgrid=False,
            tickfont=dict(color="#fdfefe", size=10),
            type="category",
        )
        fig_summary.update_yaxes(
            row=1,
            col=c_idx,
            showline=False,
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=True,
            tickfont=dict(color="#fdfefe"),
            range=[0, max_y_value_summary],  # Unified y-axis range for summary
        )
    output_figures.append(fig_summary)

    # --- Subsequent Figures: Machine Data (3 machines per figure/row) ---
    sorted_machines_df = pd.DataFrame()
    if not all_machine_df.empty and all(
        col in all_machine_df.columns for col in metrics_db_keys + ["machine_name"]
    ):
        try:
            for col in metrics_db_keys:
                all_machine_df[col] = pd.to_numeric(
                    all_machine_df[col], errors="coerce"
                )
            all_machine_df = all_machine_df.fillna(0)
            all_machine_df["total_consumption"] = all_machine_df[metrics_db_keys].sum(
                axis=1
            )
            sorted_machines_df = all_machine_df.sort_values(
                by=["total_consumption", "machine_name"], ascending=[True, True]
            ).reset_index(drop=True)
        except Exception as e:
            logger.error(f"Error sorting machines for '{period}': {e}")
    elif not all_machine_df.empty:
        logger.warning(
            f"Required columns missing in 'all_machine' for '{period}'. No machine plots."
        )

    num_machines = len(sorted_machines_df)
    for i in range(0, num_machines, machines_per_row_fig):
        chunk_df = sorted_machines_df.iloc[i : i + machines_per_row_fig]
        num_in_chunk = len(chunk_df)

        machine_row_fig_height = row_height_px
        if title_font_size:
            machine_row_fig_height += (
                title_font_size + 10
            )  # Main title for machine fig row
        if subplot_title_font_size:
            machine_row_fig_height += (
                subplot_title_font_size + 5
            )  # Subplot titles (machine names)

        machine_subplot_titles = [""] * machines_per_row_fig
        for j in range(num_in_chunk):
            m_name = str(chunk_df.iloc[j]["machine_name"])
            machine_subplot_titles[j] = (
                m_name if len(m_name) < 30 else m_name[:27] + "..."
            )

        fig_machine_row = make_subplots(
            rows=1,
            cols=machines_per_row_fig,
            subplot_titles=machine_subplot_titles,
            horizontal_spacing=0.04,
        )

        for j in range(num_in_chunk):
            machine_data_for_plot = chunk_df.iloc[[j]][metrics_db_keys].copy()
            _add_bar_traces_for_category_subplot(
                fig_machine_row,
                machine_data_for_plot,
                lang,
                1,
                j + 1,
                False,
                machine_subplot_titles[j],
            )

        machine_row_main_title = f"{current_lang_opts['main_title']} - {period} (Machines {i+1}-{min(i+num_in_chunk, num_machines)})"
        machine_row_layout_args = dict(
            title_text=machine_row_main_title,
            title_x=0.5,
            title_font_size=title_font_size,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            height=machine_row_fig_height,
            margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
        )
        if plot_width:
            machine_row_layout_args.update({"width": plot_width, "autosize": False})
        else:
            machine_row_layout_args["autosize"] = True
        fig_machine_row.update_layout(**machine_row_layout_args)
        fig_machine_row.update_annotations(
            font_size=subplot_title_font_size
        )  # For machine names as subplot titles

        for j in range(
            num_in_chunk
        ):  # Axes for machine fig row (only for plotted machines)
            fig_machine_row.update_xaxes(
                row=1,
                col=j + 1,
                showline=True,
                linewidth=1,
                linecolor="#fdfefe",
                showgrid=False,
                tickfont=dict(color="#fdfefe", size=10),
                type="category",
            )
            fig_machine_row.update_yaxes(
                row=1,
                col=j + 1,
                showline=False,
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.2)",
                zeroline=True,
                tickfont=dict(color="#fdfefe"),
                rangemode="tozero",
            )
        output_figures.append(fig_machine_row)

    if (
        not output_figures
    ):  # Should only happen if even summary fig failed (which implies error list was already returned)
        logger.warning(
            f"No figures generated for chart4_figure_detail, '{period}'. Returning error."
        )
        return _create_error_figure_list(f"No Data to Display: {period}")

    return output_figures
