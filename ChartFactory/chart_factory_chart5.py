import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Language options for titles and labels
lang_option_chart5 = {
    "en": {
        "main_title": "Machine Activity Timeline",
        "time_axis_title": "Time",
        "machine_axis_title": "Machine",
        "current_time_label": "Current Time",
        "no_data_message": "No activity data to display.",
        "error_message_header": "Data Error for Timeline",
    },
    "zh_hk": {
        "main_title": "設備活動時間線",
        "time_axis_title": "時間",
        "machine_axis_title": "設備",
        "current_time_label": "現在時間",
        "no_data_message": "沒有活動數據顯示。",
        "error_message_header": "時間線數據錯誤",
    },
    "zh_cn": {
        "main_title": "设备活动时间线",
        "time_axis_title": "时间",
        "machine_axis_title": "设备",
        "current_time_label": "当前时间",
        "no_data_message": "无活动数据显示。",
        "error_message_header": "时间线数据错误",
    },
}


def _int_to_hex_color(color_int: int) -> str:
    """Converts an integer color (potentially signed, from ARGB) to #RRGGBB hex string."""
    if color_int is None or pd.isna(
        color_int
    ):  # Check for pd.NA or np.nan if applicable
        return "#808080"  # Default grey for missing color
    try:
        color_int = int(color_int)  # Ensure it's a Python int
        return f"#{color_int & 0xFFFFFF:06x}"
    except (ValueError, TypeError):
        logger.warning(
            f"Invalid color value encountered: {color_int}. Using default grey."
        )
        return "#808080"


def _format_datetime_for_hover(dt_obj):
    if pd.isna(dt_obj):
        return "N/A"
    # Ensure dt_obj is a datetime object before formatting
    if isinstance(dt_obj, (datetime, pd.Timestamp)):
        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt_obj)  # Fallback if not a datetime object


def create_chart5_figure(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    lang: str = "zh_cn",
    margin_top: int = 60,
    margin_bottom: int = 60,
    margin_left: int = 100,  # Increased for machine names
    margin_right: int = 40,
    row_height_px: int = 400,  # Default height
    plot_width: Optional[int] = None,
) -> go.Figure:
    current_lang_opts = lang_option_chart5.get(lang, lang_option_chart5["zh_cn"])

    def _create_error_figure(message: str, is_no_data: bool = False) -> go.Figure:
        fig_error = go.Figure()
        title = message
        if is_no_data:
            title = current_lang_opts["no_data_message"]

        layout_args = dict(
            title_text=title,
            title_x=0.5,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            xaxis_visible=False,
            yaxis_visible=False,
            height=row_height_px,
        )
        if plot_width is not None:
            layout_args["width"] = plot_width
            layout_args["autosize"] = False
        else:
            layout_args["autosize"] = True
        fig_error.update_layout(**layout_args)
        if not is_no_data:
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
            or "all_machine" not in dfs[period]
        ):
            logger.error(
                f"Data for period '{period}' is missing 'all_machine' key or not structured correctly for chart5."
            )
            return _create_error_figure(
                f"{current_lang_opts['error_message_header']}: {period} - Invalid Structure"
            )

        df_orig = dfs[period]["all_machine"]

        if df_orig is None or df_orig.empty:
            logger.info(f"No data available for chart5, period '{period}'.")
            return _create_error_figure(
                current_lang_opts["no_data_message"], is_no_data=True
            )

        required_cols = [
            "machine_name",
            "start_time",
            "expected_run_minutes",
            "color",
            "batch_no",
            "state",
        ]
        if not all(col in df_orig.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df_orig.columns]
            logger.error(
                f"DataFrame for chart5 period '{period}' is missing required columns: {missing}. Found: {df_orig.columns.tolist()}"
            )
            return _create_error_figure(
                f"{current_lang_opts['error_message_header']}: {period} - Missing Columns: {', '.join(missing)}"
            )

        df = df_orig.copy()

        # Data type conversions and calculations
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["expected_run_minutes"] = pd.to_numeric(
            df["expected_run_minutes"], errors="coerce"
        )

        # Handle 'color' separately for potential NaNs before int conversion in _int_to_hex_color
        # df["color"] is used directly by _int_to_hex_color which handles None/NaN

        df.dropna(
            subset=[
                "start_time",
                "expected_run_minutes",
                "machine_name",
                "color",
                "state",
            ],
            inplace=True,
        )

        if df.empty:
            logger.info(
                f"Data became empty after cleaning for chart5, period '{period}'."
            )
            return _create_error_figure(
                current_lang_opts["no_data_message"], is_no_data=True
            )

        df["expected_end_time"] = df.apply(
            lambda row: row["start_time"]
            + timedelta(minutes=row["expected_run_minutes"]),
            axis=1,
        )
        df["hex_color"] = df["color"].apply(_int_to_hex_color)
        df["duration_timedelta"] = df["expected_run_minutes"].apply(
            lambda x: timedelta(minutes=x)
        )

        df.sort_values(by=["machine_name", "start_time"], inplace=True)

        df["start_numeric"] = df["start_time"].astype(int) // 10**6  # to milliseconds
        df["duration_numeric"] = (
            df["duration_timedelta"].dt.total_seconds() * 1000
        )  # to milliseconds

        if "action_name" not in df.columns:
            df["action_name"] = "Activity"
        else:
            df["action_name"] = df["action_name"].fillna("Activity")

    except Exception as e:
        logger.error(
            f"Unexpected error preparing data for chart5, period '{period}': {str(e)}",
            exc_info=True,
        )
        return _create_error_figure(
            f"{current_lang_opts['error_message_header']}: {period} - Unexpected Data Prep Error"
        )

    fig = go.Figure()
    # TODO change back to now
    # now = pd.Timestamp("2025-04-07 05:00:00")
    now = pd.Timestamp.now()

    # Group activities by machine and create one trace per machine
    unique_machines = df["machine_name"].unique().tolist()

    # Define state colors
    state_colors = {
        "行机": "#2ecc71",
        "停机": "#e74c3c",
        "暂停": "#f1c40f",
        "关机": "#e74c3c",
        "维修": "#3498db",
    }

    # Create machine display names with states and collect state colors
    machine_display_names = []
    machine_state_colors = []

    for machine_name in unique_machines:
        machine_df = df[df["machine_name"] == machine_name].copy()
        # Use the first state for this machine
        first_state = machine_df.iloc[0]["state"]
        display_name = f"{machine_name}"
        machine_display_names.append(display_name)

        # Get color for this state, default to white if state not found
        state_color = state_colors.get(first_state, "#ffffff")
        machine_state_colors.append(state_color)

    for i, machine_name in enumerate(unique_machines):
        machine_df = df[df["machine_name"] == machine_name].copy()
        machine_df = machine_df.sort_values("start_time")
        display_name = machine_display_names[i]

        # Prepare arrays for this machine's segments
        base_times = []
        durations = []
        colors = []
        hover_texts = []
        batch_texts = []

        for _, row in machine_df.iterrows():
            base_times.append(row["start_numeric"])
            durations.append(row["duration_numeric"])
            colors.append(row["hex_color"])
            batch_texts.append(str(row.get("batch_no", "")))

            hover_text = (
                f"<b>{row['machine_name']}</b><br>"
                f"State: {row['state']}<br>"
                f"Action: {row.get('action_name', 'N/A')}<br>"
                f"Start: {_format_datetime_for_hover(row['start_time'])}<br>"
                f"End: {_format_datetime_for_hover(row['expected_end_time'])}<br>"
                f"Duration: {row['expected_run_minutes']:.0f} min"
            )
            hover_texts.append(hover_text)

        # Create one Bar trace for this machine with multiple segments
        fig.add_trace(
            go.Bar(
                y=[display_name] * len(base_times),  # Use display name with state
                base=base_times,  # Array of start times
                x=durations,  # Array of durations
                orientation="h",
                width=0.7,
                marker_color=colors,  # Array of colors for each segment
                name=display_name,
                text=batch_texts,  # Array of batch numbers
                # textfont=dict(size=12),
                textposition="inside",
                insidetextanchor="middle",
                hovertext=hover_texts,  # Array of hover texts
                hoverinfo="text",
                showlegend=False,  # Don't show in legend to avoid clutter
            )
        )

    now_numeric = now.timestamp() * 1000

    if period == "24_hrs":
        min_time_boundary = now - timedelta(hours=12)
        max_time_boundary = now + timedelta(hours=12)
    elif period == "48_hrs":
        min_time_boundary = now - timedelta(hours=24)
        max_time_boundary = now + timedelta(hours=24)
    elif period == "72_hrs":
        min_time_boundary = now - timedelta(hours=24)
        max_time_boundary = now + timedelta(hours=48)
    else:
        logger.warning(f"Unknown period '{period}' for chart5, defaulting to 24_hrs.")
        min_time_boundary = now - timedelta(hours=12)
        max_time_boundary = now + timedelta(hours=12)

    min_time_numeric = min_time_boundary.timestamp() * 1000
    max_time_numeric = max_time_boundary.timestamp() * 1000

    fig.add_vline(
        x=now_numeric,
        line_width=2,
        line_dash="dash",
        line_color="#fdfefe",
        # annotation_text=current_lang_opts["current_time_label"],
        # annotation_position="top right",
        # annotation_font_size=10,
        # annotation_font_color="red",
    )

    fig.update_layout(
        title_text=f"{current_lang_opts['main_title']} - {period}",
        title_x=0.5,
        # xaxis_title=current_lang_opts["time_axis_title"],
        # yaxis_title=current_lang_opts["machine_axis_title"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#fdfefe",
        margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
        showlegend=False,
        barcornerradius=50,
    )

    num_unique_machines = len(unique_machines)

    # Dynamic height calculation
    # Base height + per machine height + top/bottom margins
    bar_slot_height = 25  # estimated pixels needed per machine row for bar + padding
    calculated_plot_area_height = num_unique_machines * bar_slot_height
    dynamic_fig_height = (
        margin_top + margin_bottom + calculated_plot_area_height + 50
    )  # 50 for x-axis, title etc.

    final_height = max(
        row_height_px, dynamic_fig_height if num_unique_machines > 0 else row_height_px
    )

    if plot_width:
        fig.update_layout(width=plot_width, autosize=False, height=final_height)
    else:
        fig.update_layout(autosize=True, height=final_height)

    time_span_hours = (max_time_boundary - min_time_boundary).total_seconds() / 3600
    if time_span_hours <= 1:
        tick_freq_str = "15min"
        tick_format_str = "%H:%M"
    elif time_span_hours <= 6:
        tick_freq_str = "H"
        tick_format_str = "%H:%M"
    elif time_span_hours <= 12:
        tick_freq_str = "2H"  # Changed from 'H' for less clutter
        tick_format_str = "%H:%M"
    elif time_span_hours <= 24:
        tick_freq_str = "3H"
        tick_format_str = "%H:%M"
    elif time_span_hours <= 48:
        tick_freq_str = "6H"
        tick_format_str = "%m-%d %H:%M"
    else:  # More than 48 hours (e.g. 72h span)
        tick_freq_str = "12H"
        tick_format_str = "%m-%d %H:%M"

    # Generate ticks ensuring they start reasonably
    # Ensure tick_dt_values are timezone-naive if min/max_time_boundary are naive.
    tick_dt_values_naive = pd.date_range(
        start=min_time_boundary.round("H"),
        end=max_time_boundary.round("H"),
        freq=tick_freq_str,
    )

    custom_tickvals = [
        t.timestamp() * 1000
        for t in tick_dt_values_naive
        if min_time_boundary <= t <= max_time_boundary
    ]
    custom_ticktext = [
        t.strftime(tick_format_str)
        for t in tick_dt_values_naive
        if min_time_boundary <= t <= max_time_boundary
    ]

    # Helper to determine if a datetime is aligned to the current tick frequency
    def _is_boundary_aligned(dt: datetime, freq_str: str) -> bool:
        """Return True if *dt* falls exactly on a tick boundary determined by *freq_str*."""
        try:
            freq_str = freq_str.strip()
            # Minute-based frequency, e.g. "15min"
            if freq_str.lower().endswith("min"):
                interval_min = int(freq_str[:-3])
                return (
                    dt.second == 0
                    and dt.microsecond == 0
                    and dt.minute % interval_min == 0
                )
            # Hour-based frequency, e.g. "H", "2H", "3H", "6H", "12H"
            if freq_str.upper().endswith("H"):
                hours_part = freq_str[:-1]
                interval_hr = int(hours_part) if hours_part else 1
                return (
                    dt.minute == 0
                    and dt.second == 0
                    and dt.microsecond == 0
                    and dt.hour % interval_hr == 0
                )
        except Exception:
            # Any parsing issue → treat as not aligned
            pass
        return False

    include_max_boundary = _is_boundary_aligned(max_time_boundary, tick_freq_str)

    # ----- MIN BOUNDARY TICK HANDLING -----
    # Always consider the min boundary tick (e.g. 12 h before *now*). Add it unless the
    # next tick is closer than 1 hour, in which case we skip it to avoid overlapping labels.
    ONE_HOUR_MS = 3600 * 1000

    if min_time_numeric not in custom_tickvals:
        if not custom_tickvals:
            # No other ticks – simply add the boundary tick.
            custom_tickvals.insert(0, min_time_numeric)
            custom_ticktext.insert(0, min_time_boundary.strftime(tick_format_str))
        else:
            distance_to_next = custom_tickvals[0] - min_time_numeric
            if distance_to_next >= ONE_HOUR_MS:
                custom_tickvals.insert(0, min_time_numeric)
                custom_ticktext.insert(0, min_time_boundary.strftime(tick_format_str))

    # ----- MAX BOUNDARY TICK HANDLING -----
    # Keep existing behaviour: add only if boundary aligns with tick frequency & it's missing.
    if include_max_boundary and (
        not custom_tickvals or custom_tickvals[-1] < max_time_numeric
    ):
        custom_tickvals.append(max_time_numeric)
        custom_ticktext.append(max_time_boundary.strftime(tick_format_str))

    # Ensure at least one tick exists; if the list became empty for some reason, fall back to
    # the nearest aligned tick after the min boundary to guarantee visible ticks.
    if not custom_tickvals:
        fallback_tick = (
            min_time_boundary + (max_time_boundary - min_time_boundary) / 2
        ).timestamp() * 1000
        custom_tickvals = [fallback_tick]
        custom_ticktext = [
            datetime.fromtimestamp(fallback_tick / 1000).strftime(tick_format_str)
        ]

    # Remove duplicate tick values that might arise from adding boundaries
    final_ticks = {}
    for val, text in zip(custom_tickvals, custom_ticktext):
        if val not in final_ticks:  # Keep first occurrence for text
            final_ticks[val] = text

    sorted_final_tickvals = sorted(final_ticks.keys())
    sorted_final_ticktext = [final_ticks[val] for val in sorted_final_tickvals]

    fig.update_xaxes(
        type="linear",
        range=[min_time_numeric, max_time_numeric],
        tickvals=sorted_final_tickvals if sorted_final_tickvals else None,
        ticktext=sorted_final_ticktext if sorted_final_tickvals else None,
        showline=True,
        linewidth=1,
        linecolor="#fdfefe",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        tickfont=dict(color="#fdfefe", size=10),
    )

    fig.update_yaxes(
        type="category",
        categoryorder="array",
        categoryarray=machine_display_names[::-1],
        showline=True,
        linewidth=1,
        linecolor="#fdfefe",
        showgrid=False,
        tickfont=dict(color="#fdfefe", size=10),
    )

    # Update y-axis tick colors based on machine states
    fig.update_layout(
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(machine_display_names))),
            ticktext=[
                f'<span style="color:{machine_state_colors[i]}">{name}</span>'
                for i, name in enumerate(machine_display_names[::-1])
            ],
            tickfont=dict(size=14),
        )
    )

    return fig
