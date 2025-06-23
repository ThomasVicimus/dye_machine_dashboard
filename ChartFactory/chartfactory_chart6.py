import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List
import logging
import yaml
import re
from dash import html
import dash_bootstrap_components as dbc


logger = logging.getLogger(__name__)


def _make_figure_empty_looking(fig: go.Figure):
    """Helper to style a figure to look empty, used for error/empty states."""
    fig.update_layout(
        title_font_color="#fdfefe",  # Added for title text color
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_zeroline=False,
        yaxis_zeroline=False,
        xaxis_visible=False,
        yaxis_visible=False,
        annotations=[
            {
                "text": (
                    fig.layout.title.text
                    if fig.layout.title and fig.layout.title.text
                    else "No data"
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,  # Center text
                "y": 0.5,  # Center text
                "showarrow": False,
                "font": {"size": 16, "color": "#fdfefe"},  # Updated font color
            }
        ],
    )
    # Clear any existing data traces if any were added before error
    fig.data = []


def _load_reason_mapping():
    """Load the reason mapping from YAML file."""
    try:
        with open("env/chart6_reason_txt.yml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading reason mapping: {e}")
        return {}


def _extract_reason_number(reason_col):
    """Extract reason number from column name like 'reason8_hour' -> '8'."""
    try:
        # Use regex to extract the number after 'reason'
        match = re.search(r"reason(\d+)", reason_col)
        if match:
            return match.group(1)
        else:
            return reason_col
    except:
        return reason_col


def _get_reason_display_name(reason_col, reason_mapping):
    """Get display name for reason from mapping."""
    reason_number = _extract_reason_number(reason_col)
    return reason_mapping.get(reason_number, f"Reason {reason_number}")


def create_chart6_figure(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    # Optional styling parameters can be added here if needed
    # e.g., bar_color_highest: Optional[str] = None, bar_color_lowest: Optional[str] = None
) -> go.Figure:
    """
    Creates two side-by-side vertical bar charts showing stop reasons for highest and lowest machines.

    Args:
        period (str): The key for the period in the dfs dictionary (e.g., "今天").
        dfs (Dict[str, Dict[str, pd.DataFrame]]): A nested dictionary containing DataFrames.
            Expected structure: dfs[period]['highest'] and dfs[period]['lowest'] should be the target DataFrames.

    Returns:
        go.Figure: A Plotly graph object figure with two subplots. If data is invalid or missing,
                   an empty figure with an error message/note might be returned.
    """
    # Load reason mapping
    reason_mapping = _load_reason_mapping()

    # Create subplots with two columns
    fig = make_subplots(
        rows=1,
        cols=2,
        # subplot_titles=("Highest Usage Machine", "Lowest Usage Machine"),
        # specs=[[{"secondary_y": False}, {"secondary_y": False}]],
    )

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
            or "highest" not in dfs[period]
            or "lowest" not in dfs[period]
        ):
            raise KeyError(
                f"Expected path dfs[period]['highest'] and dfs[period]['lowest'] not found or 'dfs' is not structured correctly.\n {type(dfs)=}"
            )

        df_period = dfs[period]
        df_highest = df_period["highest"]
        df_lowest = df_period["lowest"]

    except KeyError as e:
        logger.error(
            f"Data not found for period '{period}' in {dfs.keys()}. Error: {e}"
        )
        fig.update_layout(title_text=f"Data not available for {period}")
        _make_figure_empty_looking(fig)
        return fig
    except TypeError as e:
        logger.error(
            f"Invalid structure for 'dfs' argument for period '{period}'. Expected Dict[str, Dict[str, pd.DataFrame]]. Error: {e}"
        )
        fig.update_layout(title_text=f"Invalid data structure for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Validate DataFrames
    if not isinstance(df_highest, pd.DataFrame) or not isinstance(
        df_lowest, pd.DataFrame
    ):
        logger.warning(
            f"Data for period '{period}' - 'highest' or 'lowest' is not a DataFrame."
        )
        fig.update_layout(title_text=f"Invalid data format for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Collect all reasons and their values from both machines
    all_reasons = (
        {}
    )  # {reason_display_name: {'highest': value, 'lowest': value, 'reason_code': code}}

    machine_name_highest = "Unknown"
    machine_name_lowest = "Unknown"

    # First pass: collect all unique reasons from both machines
    unique_reasons = set()

    # Process highest machine data
    if not df_highest.empty:
        machine_name_highest = (
            df_highest.iloc[0].get("machine_name", "Unknown")
            if len(df_highest) > 0
            else "Unknown"
        )

        # Get all reason columns (excluding machine_name and idle_hour)
        reason_columns = [col for col in df_highest.columns if col.startswith("reason")]

        for reason_col in reason_columns:
            value = df_highest.iloc[0][reason_col]
            if pd.notna(value) and value != 0:
                display_name = _get_reason_display_name(reason_col, reason_mapping)
                unique_reasons.add(display_name)
                if display_name not in all_reasons:
                    all_reasons[display_name] = {
                        "highest": 0,
                        "lowest": 0,
                        "reason_code": reason_col,
                    }
                all_reasons[display_name]["highest"] = value

    # Process lowest machine data
    if not df_lowest.empty:
        machine_name_lowest = (
            df_lowest.iloc[0].get("machine_name", "Unknown")
            if len(df_lowest) > 0
            else "Unknown"
        )

        # Get all reason columns (excluding machine_name and idle_hour)
        reason_columns = [col for col in df_lowest.columns if col.startswith("reason")]

        for reason_col in reason_columns:
            value = df_lowest.iloc[0][reason_col]
            if pd.notna(value) and value != 0:
                display_name = _get_reason_display_name(reason_col, reason_mapping)
                unique_reasons.add(display_name)
                if display_name not in all_reasons:
                    all_reasons[display_name] = {
                        "highest": 0,
                        "lowest": 0,
                        "reason_code": reason_col,
                    }
                all_reasons[display_name]["lowest"] = value

    # Create consistent color mapping for all unique reasons
    colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FFEAA7",
        "#F39C12",
        "#9B59B6",
        "#E74C3C",
        "#2ECC71",
        "#3498DB",
    ]
    sorted_reasons = sorted(unique_reasons)  # Sort for consistent order
    color_mapping = {
        reason: colors[i % len(colors)] for i, reason in enumerate(sorted_reasons)
    }

    # Create bars for each reason
    for reason_display, values in all_reasons.items():
        color = color_mapping[reason_display]

        # Add bar for highest machine (only if value > 0)
        if values["highest"] > 0:
            fig.add_trace(
                go.Bar(
                    x=[reason_display],
                    y=[values["highest"]],
                    name=reason_display,
                    marker_color=color,
                    text=[values["highest"]],
                    textposition="auto",
                    legendgroup=reason_display,  # Group legend entries
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

        # Add bar for lowest machine (only if value > 0)
        if values["lowest"] > 0:
            fig.add_trace(
                go.Bar(
                    x=[reason_display],
                    y=[values["lowest"]],
                    name=reason_display,
                    marker_color=color,
                    text=[values["lowest"]],
                    textposition="auto",
                    legendgroup=reason_display,  # Group legend entries
                    showlegend=False,  # Don't show duplicate legend
                ),
                row=1,
                col=2,
            )

    # Update layout
    fig.update_layout(
        # title_text=f"Stop Reasons Analysis - {period}<br><sub>Highest: {machine_name_highest} | Lowest: {machine_name_lowest}</sub>",
        # title_font_color="#fdfefe",
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="top",
            y=-0.15,  # Position below the plot
            xanchor="center",
            x=0.5,
            font=dict(color="#fdfefe"),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fdfefe"),
        autosize=True,
    )

    # Find the maximum value across all data to ensure consistent y-axis scaling
    max_value = 0
    for values in all_reasons.values():
        max_value = max(max_value, values["highest"], values["lowest"])

    # Add some padding to the y-axis (10% above max value)
    y_max = max_value * 1.1 if max_value > 0 else 10

    # Update x and y axes for both subplots with consistent scaling
    fig.update_yaxes(
        # title_text="Hours",
        # title_font_color="#fdfefe",
        # tickfont=dict(color="#fdfefe"),
        range=[0, y_max],  # Set same range for both subplots
        row=1,
        col=1,
    )
    fig.update_yaxes(
        # title_text="Hours",
        # title_font_color="#fdfefe",
        # tickfont=dict(color="#fdfefe"),
        range=[0, y_max],  # Set same range for both subplots
        row=1,
        col=2,
    )

    # fig.update_xaxes(
    #     title_text="Stop Reasons",
    #     title_font_color="#fdfefe",
    #     tickfont=dict(color="#fdfefe"),
    #     row=1,
    #     col=1,
    # )
    # fig.update_xaxes(
    #     title_text="Stop Reasons",
    #     title_font_color="#fdfefe",
    #     tickfont=dict(color="#fdfefe"),
    #     row=1,
    #     col=2,
    # )

    # If no reasons found, show empty state
    if not all_reasons:
        logger.warning(f"No stop reasons found for period '{period}'.")
        fig.update_layout(title_text=f"No data to display for {period}")
        _make_figure_empty_looking(fig)

    return fig


def create_chart6_txt_cards(period: str, dfs: Dict[str, Dict[str, pd.DataFrame]]):
    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
            or "highest" not in dfs[period]
            or "lowest" not in dfs[period]
            or "overall" not in dfs[period]
        ):
            raise KeyError(
                f"Expected path dfs[period]['highest'], dfs[period]['lowest'], and dfs[period]['overall'] not found or 'dfs' is not structured correctly.\n {type(dfs)=}"
            )
        df_period = dfs[period]
        df_highest = df_period["highest"]
        df_lowest = df_period["lowest"]
        df_overall = df_period["overall"]
    except KeyError as e:
        logger.error(
            f"Data not found for period '{period}' in {dfs.keys()} and keys 'highest', 'lowest', 'overall' in {df_period.keys()}. Error: {e}"
        )
        # Return empty cards if there's an error
        return (
            html.Div("Error loading data"),
            html.Div("Error loading data"),
        )

    # Extract data for card1 from overall dataframe
    # total_idle_hour = 0
    # avg_per_machine = 0

    if not df_overall.empty:
        total_idle_hour = df_overall.iloc[0].get("total_idle_hour", 0)
        avg_per_machine = df_overall.iloc[0].get("avg_per_machine", 0)

    # Extract data for cards 2 and 3
    highest_machine_name = "Unknown"
    highest_machine_hours = 0
    lowest_machine_name = "Unknown"
    lowest_machine_hours = 0

    # Get data from highest machine
    if not df_highest.empty and "idle_hour" in df_highest.columns:
        highest_machine_name = df_highest.iloc[0].get("machine_name", "Unknown")
        highest_machine_hours = df_highest.iloc[0].get("idle_hour", 0)

    # Get data from lowest machine
    if not df_lowest.empty and "idle_hour" in df_lowest.columns:
        lowest_machine_name = df_lowest.iloc[0].get("machine_name", "Unknown")
        lowest_machine_hours = df_lowest.iloc[0].get("idle_hour", 0)

    # * Card1 - Overall Statistics (Large card)
    card1 = dbc.CardBody(
        [
            html.Div(
                f"{period} 整体统计",
                style={
                    "color": "#fdfefe",
                    "fontSize": 18,
                    "fontWeight": "bold",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        "总待机时数",
                        style={
                            "color": "#fdfefe",
                            "fontSize": 14,
                            "marginBottom": "5px",
                        },
                    ),
                    html.Div(
                        f"{round(total_idle_hour, 1)}h",
                        style={
                            "color": "#2ecc71",
                            "fontSize": 24,
                            "fontWeight": "bold",
                            "marginBottom": "25px",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        "平均待机时数",
                        style={
                            "color": "#fdfefe",
                            "fontSize": 14,
                            "marginBottom": "5px",
                        },
                    ),
                    html.Div(
                        f"{round(avg_per_machine, 1)}h",
                        style={
                            "color": "#3498db",
                            "fontSize": 24,
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
        ],
        style={
            "textAlign": "center",
            "backgroundColor": "#202020",
            "fontSize": 14,
            "height": "100%",
            "minHeight": "200px",
            "padding": "20px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
        },
    )

    # * Card2 - Highest Usage Machine (Small card)
    card2_content = dbc.CardBody(
        [
            html.Div(
                f"最长待机机台",
                style={"color": "#fdfefe", "textAlign": "center"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(f"{highest_machine_name}", style={"color": "#2ecc71"}),
                        width=6,
                        className="text-start",
                    ),
                    dbc.Col(
                        html.Div(
                            f"{round(highest_machine_hours, 1)}h",
                            style={"color": "#3498db"},
                        ),
                        width=6,
                        className="text-end",
                    ),
                ],
                className="gx-0",
            ),
        ],
        style={
            "backgroundColor": "#202020",
            "fontSize": 14,
            "height": "auto",
            "maxHeight": "50px",
            "padding": "4px",
        },
    )

    # * Card3 - Lowest Usage Machine (Small card)
    card3_content = dbc.CardBody(
        [
            html.Div(
                f"最短待机机台",
                style={"color": "#fdfefe", "textAlign": "center"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(f"{lowest_machine_name}", style={"color": "#f1c40f"}),
                        width=6,
                        className="text-start",
                    ),
                    dbc.Col(
                        html.Div(
                            f"{round(lowest_machine_hours, 1)}h",
                            style={"color": "#3498db"},
                        ),
                        width=6,
                        className="text-end",
                    ),
                ],
                className="gx-0",
            ),
        ],
        style={
            "backgroundColor": "#202020",
            "fontSize": 14,
            "height": "auto",
            "maxHeight": "50px",
            "padding": "4px",
        },
    )

    # * Combined Cards 2+3 Element
    combined_cards = dbc.Row(
        [
            dbc.Col(
                dbc.Card(card3_content, className="h-100"),
                width=6,
            ),
            dbc.Col(
                dbc.Card(card2_content, className="h-100"),
                width=6,
            ),
        ],
        className="mb-2 g-2",
        style={"height": "auto", "maxHeight": "60px"},
    )

    return card1, combined_cards


def create_chart6_figure_mobile(period: str, dfs: Dict[str, Dict[str, pd.DataFrame]]):
    return create_chart6_figure(period, dfs)


def create_chart6_figure_detail(period: str, dfs: Dict[str, Dict[str, pd.DataFrame]]):
    """Generate a list of detailed figures for Chart-6.

    output_figures[0]: Highest / Lowest machines – 2 sub-plots in one figure (delegated to
    `create_chart6_figure`).

    output_figures[1...N]: Machine specific stop-reason bar charts. 3 machines are plotted
    per figure (1×3 sub-plots).  For each machine only the non-zero/top reasons are
    displayed (maximum five per machine) to keep the charts clean.
    """

    # ----- Helper : error figure list ----- #
    def _create_error_figure_list(message: str) -> List[go.Figure]:
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
            text="Data Error. Check logs or data source.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.4,
            showarrow=False,
            font=dict(size=12, color="#fdfefe"),
        )
        return [fig_error]

    # Validate `dfs` structure and extract required DataFrames
    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
        ):
            return _create_error_figure_list(f"Data Structure Error: {period}")

        data_for_period = dfs[period]
        df_highest = data_for_period.get("highest")
        df_lowest = data_for_period.get("lowest")
        df_all_machine = data_for_period.get("all_machine")

        if df_highest is None or df_lowest is None:
            return _create_error_figure_list(
                f"Missing 'highest' or 'lowest' data for {period}"
            )
    except Exception as e:
        logger.error(f"Error during data prep for chart6_figure_detail: {e}")
        return _create_error_figure_list(f"Data Preparation Error: {period}")

    # Default styling / layout parameters (mirrors chart-4 detail behaviour)
    title_font_size = 16
    subplot_title_font_size = 12
    legend_font_size = 10
    margin_top = 40
    margin_bottom = 60
    margin_left = 15
    margin_right = 15
    row_height_px = 250
    plot_width = None  # Auto width

    output_figures: List[go.Figure] = []

    # ----- Figure 0 : Highest vs Lowest ----- #
    try:
        fig_summary = create_chart6_figure(period, dfs)

        # Estimate height (title + legend etc.)
        summary_fig_height = row_height_px + title_font_size + legend_font_size + 40

        summary_layout_args = dict(
            title_font_size=title_font_size,
            height=summary_fig_height,
            margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
        )
        if plot_width is not None:
            summary_layout_args.update({"width": plot_width, "autosize": False})
        else:
            summary_layout_args["autosize"] = True

        # Add subplot titles for Highest and Lowest machines
        machine_name_highest = (
            df_highest.iloc[0].get("machine_name", "Unknown")
            if df_highest is not None and not df_highest.empty
            else "Unknown"
        )
        machine_name_lowest = (
            df_lowest.iloc[0].get("machine_name", "Unknown")
            if df_lowest is not None and not df_lowest.empty
            else "Unknown"
        )

        highest_title = f"停机时数最高 - {machine_name_highest}"
        lowest_title = f"停机时数最低 - {machine_name_lowest}"

        # Remove any existing annotations (summary fig has no subplot titles by default)
        # Then add our custom titles positioned roughly above each subplot
        fig_summary.update_layout(**summary_layout_args)

        # Coordinates are approximate: x=0.25 (first subplot center), x=0.75 (second)
        fig_summary.add_annotation(
            text=lowest_title,
            x=0.75,
            y=1.08,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=subplot_title_font_size, color="#fdfefe"),
        )
        fig_summary.add_annotation(
            text=highest_title,
            x=0.25,
            y=1.08,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=subplot_title_font_size, color="#fdfefe"),
        )

        # Ensure font size of all annotations matches settings
        fig_summary.update_annotations(font_size=subplot_title_font_size)

        output_figures.append(fig_summary)
    except Exception as e:
        logger.error(f"Error creating summary fig for chart6 detail: {e}")
        return _create_error_figure_list(f"Summary Figure Error: {period}")

    # If there is no machine data, we are done.
    if df_all_machine is None or df_all_machine.empty:
        return output_figures

    # ----- Subsequent Figures : Machines (3 per row) ----- #
    machines_per_row_fig = 3

    # Sort machines – by 'idle_hour' descending if available, else by name
    if "idle_hour" in df_all_machine.columns:
        df_sorted = df_all_machine.sort_values(
            by=["idle_hour", "machine_name"], ascending=[False, True]
        ).reset_index(drop=True)
    else:
        df_sorted = df_all_machine.sort_values(by=["machine_name"]).reset_index(
            drop=True
        )

    reason_mapping = _load_reason_mapping()

    # Color palette for reasons (re-used across all figures)
    base_colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FFEAA7",
        "#F39C12",
        "#9B59B6",
        "#E74C3C",
        "#2ECC71",
        "#3498DB",
    ]

    def _get_reason_bars_for_machine(machine_row: pd.Series):
        """Return (display_names, values) for up to top-5 non-zero reasons."""
        reason_cols = [c for c in machine_row.index if str(c).startswith("reason")]
        reason_values = {}
        for col in reason_cols:
            val = machine_row[col]
            if pd.notna(val) and val != 0:
                disp = _get_reason_display_name(col, reason_mapping)
                reason_values[disp] = val

        # Take top-5 reasons by value
        sorted_items = sorted(reason_values.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        display_names = [it[0] for it in sorted_items]
        values = [it[1] for it in sorted_items]
        return display_names, values

    for i in range(0, len(df_sorted), machines_per_row_fig):
        chunk_df = df_sorted.iloc[i : i + machines_per_row_fig]
        num_in_chunk = len(chunk_df)

        # Determine subplot titles (machine names) & aggregate unique reasons for color map
        subplot_titles = []
        unique_reasons_chunk = set()
        for idx in range(num_in_chunk):
            m_name = str(chunk_df.iloc[idx].get("machine_name", f"M{idx+1}"))
            subplot_titles.append(m_name if len(m_name) < 30 else m_name[:27] + "...")

            dn, _ = _get_reason_bars_for_machine(chunk_df.iloc[idx])
            unique_reasons_chunk.update(dn)

        sorted_reasons_chunk = sorted(unique_reasons_chunk)
        color_mapping_chunk = {
            reason: base_colors[j % len(base_colors)]
            for j, reason in enumerate(sorted_reasons_chunk)
        }

        # Build figure for this set of machines
        fig_machine_row = make_subplots(
            rows=1,
            cols=num_in_chunk,
            subplot_titles=subplot_titles,
            horizontal_spacing=0.04,
        )

        first_subplot = True  # To control legend duplicates
        max_y_val_chunk = 0.0

        for j in range(num_in_chunk):
            row_series = chunk_df.iloc[j]
            x_vals, y_vals = _get_reason_bars_for_machine(row_series)

            max_y_val_chunk = max(max_y_val_chunk, max(y_vals) if y_vals else 0)

            for k, reason_name in enumerate(x_vals):
                fig_machine_row.add_trace(
                    go.Bar(
                        x=[reason_name],
                        y=[y_vals[k]],
                        name=reason_name,
                        marker_color=color_mapping_chunk.get(
                            reason_name, base_colors[k % len(base_colors)]
                        ),
                        legendgroup=reason_name,
                        showlegend=first_subplot,
                        text=[y_vals[k]],
                        textposition="auto",
                    ),
                    row=1,
                    col=j + 1,
                )
            first_subplot = False  # Legend only for first subplot

        # Y-axis scaling
        y_max = max_y_val_chunk * 1.1 if max_y_val_chunk > 0 else 10
        for col_idx in range(1, num_in_chunk + 1):
            fig_machine_row.update_yaxes(range=[0, y_max], row=1, col=col_idx)
            fig_machine_row.update_xaxes(type="category", row=1, col=col_idx)

        # Layout for this figure
        machine_row_fig_height = row_height_px + title_font_size + legend_font_size + 40
        machine_row_layout_args = dict(
            title_text=f"{period} Stop Reasons – Machines {i+1}-{i+num_in_chunk}",
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
            height=machine_row_fig_height,
            margin=dict(t=margin_top, b=margin_bottom, l=margin_left, r=margin_right),
        )
        if plot_width is not None:
            machine_row_layout_args.update({"width": plot_width, "autosize": False})
        else:
            machine_row_layout_args["autosize"] = True

        fig_machine_row.update_layout(**machine_row_layout_args)
        fig_machine_row.update_annotations(font_size=subplot_title_font_size)

        output_figures.append(fig_machine_row)

    if not output_figures:
        logger.warning(
            f"No figures generated for chart6_figure_detail, '{period}'. Returning error."
        )
        return _create_error_figure_list(f"No Data to Display: {period}")

    return output_figures
