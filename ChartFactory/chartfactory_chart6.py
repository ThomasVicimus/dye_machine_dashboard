import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional
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
        period (str): The key for the period in the dfs dictionary (e.g., "今日").
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

        # Get all reason columns (excluding machine_name and sum_hour)
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

        # Get all reason columns (excluding machine_name and sum_hour)
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
    total_sum_hour = 0
    avg_per_machine = 0

    if not df_overall.empty:
        total_sum_hour = df_overall.iloc[0].get("total_sum_hour", 0)
        avg_per_machine = df_overall.iloc[0].get("avg_per_machine", 0)

    # Extract data for cards 2 and 3
    highest_machine_name = "Unknown"
    highest_machine_hours = 0
    lowest_machine_name = "Unknown"
    lowest_machine_hours = 0

    # Get data from highest machine
    if not df_highest.empty and "sum_hour" in df_highest.columns:
        highest_machine_name = df_highest.iloc[0].get("machine_name", "Unknown")
        highest_machine_hours = df_highest.iloc[0].get("sum_hour", 0)

    # Get data from lowest machine
    if not df_lowest.empty and "sum_hour" in df_lowest.columns:
        lowest_machine_name = df_lowest.iloc[0].get("machine_name", "Unknown")
        lowest_machine_hours = df_lowest.iloc[0].get("sum_hour", 0)

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
                        f"{round(total_sum_hour, 1)}h",
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
                dbc.Card(card2_content, className="h-100"),
                width=6,
            ),
            dbc.Col(
                dbc.Card(card3_content, className="h-100"),
                width=6,
            ),
        ],
        className="mb-2 g-2",
        style={"height": "auto", "maxHeight": "60px"},
    )

    return card1, combined_cards


def create_chart6_figure_mobile(period: str, dfs: Dict[str, Dict[str, pd.DataFrame]]):
    return create_chart6_figure(period, dfs, mobile=True)
