import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional
import logging
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


def create_chart3_figure(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
    # Optional styling parameters can be added here if needed
    # e.g., line_color: Optional[str] = None, marker_symbol: Optional[str] = None
) -> go.Figure:
    """
    Creates a line chart showing trend over time for 'weight_kg' against 'mmdd'.

    Args:
        period (str): The key for the period in the dfs dictionary (e.g., "last_7_days").
        dfs (Dict[str, Dict[str, pd.DataFrame]]): A nested dictionary containing DataFrames.
            Expected structure: dfs[period]['all_machine'] should be the target DataFrame.

    Returns:
        go.Figure: A Plotly graph object figure. If data is invalid or missing,
                   an empty figure with an error message/note might be returned.
    """
    fig = go.Figure()  # Initialize an empty figure

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
            or "all_machine" not in dfs[period]
        ):
            raise KeyError(
                f"Expected path dfs[period]['all_machine'] not found or 'dfs' is not structured correctly.\n {type(dfs)=}"
            )
        df_period = dfs[period]
        df = df_period["all_machine"]
    except KeyError as e:
        logger.error(
            f"Data not found for period '{period}' in {dfs.keys()} and key 'all_machine' in {df_period.keys()}. Error: {e}"
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

    if not isinstance(df, pd.DataFrame):
        logger.warning(
            f"Data for period '{period}' and key 'all_machine' is not a DataFrame."
        )
        fig.update_layout(title_text=f"Invalid data format for {period}")
        _make_figure_empty_looking(fig)
        return fig

    if df.empty:
        logger.warning(
            f"DataFrame for period '{period}' and key 'all_machine' is empty."
        )
        fig.update_layout(title_text=f"No data to display for {period}")
        _make_figure_empty_looking(fig)
        return fig

    required_cols = ["mmdd", "weight_kg"]
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        logger.error(
            f"Missing required columns {missing_cols} in DataFrame for period '{period}'."
        )
        fig.update_layout(title_text=f"Error: Missing data columns for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Ensure 'weight_kg' is numeric
    df_copy = df.copy()  # Work on a copy to avoid SettingWithCopyWarning
    # * Process df
    df_copy = df_copy.groupby(["mmdd"])["weight_kg"].sum().reset_index()
    try:
        df_copy["weight_kg"] = pd.to_numeric(df_copy["weight_kg"], errors="coerce")
        if df_copy["weight_kg"].isnull().all():
            logger.error(
                f"'weight_kg' column for period '{period}' contains no valid numeric data after conversion."
            )
            fig.update_layout(title_text=f"Invalid 'weight_kg' data for {period}")
            _make_figure_empty_looking(fig)
            return fig
        # Drop rows where 'weight_kg' became NaN if partial data is acceptable,
        # or handle as per application requirements.
        df_copy.dropna(subset=["weight_kg"], inplace=True)
        if df_copy.empty:
            logger.warning(
                f"DataFrame became empty after dropping NaNs in 'weight_kg' for period '{period}'."
            )
            fig.update_layout(title_text=f"No valid 'weight_kg' data for {period}")
            _make_figure_empty_looking(fig)
            return fig

        # Calculate y-axis upper bound for padding
        max_y_value = df_copy["weight_kg"].max()
        if pd.notna(max_y_value):
            yaxis_upper_bound = max_y_value * 1.3 if max_y_value > 0 else 10.0
        else:  # Fallback if max_y_value is NaN (e.g. df became all NaNs then empty)
            yaxis_upper_bound = 10.0

    except Exception as e:
        logger.error(
            f"Error converting 'weight_kg' to numeric for period '{period}': {e}"
        )
        fig.update_layout(title_text=f"Error in 'weight_kg' data for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Determine text labels based on number of data points
    text_values = []  # Default to empty list
    if not df_copy.empty:
        if len(df_copy) > 7:
            text_values = [""] * len(df_copy)  # Initialize with empty strings

            current_max_val = df_copy["weight_kg"].max()
            current_min_val = df_copy["weight_kg"].min()

            max_indices = df_copy.index[
                df_copy["weight_kg"] == current_max_val
            ].tolist()
            min_indices = df_copy.index[
                df_copy["weight_kg"] == current_min_val
            ].tolist()

            if max_indices:  # If there are any max values
                latest_max_idx = max_indices[
                    -1
                ]  # Get the index of the latest occurrence
                if 0 <= latest_max_idx < len(text_values):
                    text_values[latest_max_idx] = df_copy["weight_kg"].iloc[
                        latest_max_idx
                    ]

            if min_indices:  # If there are any min values
                latest_min_idx = min_indices[
                    -1
                ]  # Get the index of the latest occurrence
                if 0 <= latest_min_idx < len(text_values):
                    text_values[latest_min_idx] = df_copy["weight_kg"].iloc[
                        latest_min_idx
                    ]
        else:
            text_values = df_copy["weight_kg"].tolist()  # Show all texts

    fig.add_trace(
        go.Scatter(
            x=df_copy["mmdd"],
            y=df_copy["weight_kg"],
            mode="lines+markers+text",
            text=text_values,  # Use the conditionally generated text_values
            textposition="top right",
            textfont=dict(color="#fdfefe", size=12),  # Ensure color and set size
        )
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        font_color="#fdfefe",  # General text color
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis_showgrid=False,  # Remove x-axis grid
        yaxis_showgrid=False,  # Remove y-axis grid
        xaxis_showline=True,  # Show x-axis line
        yaxis_showline=True,  # Show y-axis line
        xaxis_linecolor="#fdfefe",  # Set x-axis line color
        yaxis_linecolor="#fdfefe",  # Set y-axis line color
        xaxis_tickfont=dict(color="#fdfefe"),  # X-axis tick label color
        yaxis_tickfont=dict(color="#fdfefe"),  # Y-axis tick label color
        yaxis_range=[0, yaxis_upper_bound],  # Explicitly set y-axis range
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(type="category"),  # Ensure x-axis is treated as categorical
    )

    return fig


def create_chart3_txt_cards(period: str, dfs: Dict[str, Dict[str, pd.DataFrame]]):

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
            or "all_machine" not in dfs[period]
        ):
            raise KeyError(
                f"Expected path dfs[period]['all_machine'] not found or 'dfs' is not structured correctly.\n {type(dfs)=}"
            )
        df_period = dfs[period]
        df = df_period["all_machine"]
    except KeyError as e:
        logger.error(
            f"Data not found for period '{period}' in {dfs.keys()} and key 'all_machine' in {df_period.keys()}. Error: {e}"
        )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if period == "今天":
        df = df[df["date"] == df["date"].max()]
    # * Card1
    total_prod = df["weight_kg"].sum()
    # * Card2
    max_prod_machine = df.loc[df["weight_kg"].idxmax(), "machine_name"]
    max_prod_value = df["weight_kg"].max()
    # * Card3
    min_prod_machine = df.loc[df["weight_kg"].idxmin(), "machine_name"]
    min_prod_value = df["weight_kg"].min()

    card1 = dbc.CardBody(
        [
            html.Div(
                f"{period} 总产量",
                style={"color": "#fdfefe", "fontSize": "12px", "lineHeight": "1.2"},
            ),
            html.Div(
                f"{round(total_prod)}kg",
                style={"color": "#2ecc71", "fontSize": "14px", "lineHeight": "1.2"},
            ),
        ],
        style={
            "textAlign": "center",
            "backgroundColor": "#202020",
            "height": "auto",
            "padding": "8px 4px",
            "overflow": "hidden",
        },
    )

    card2 = dbc.CardBody(
        [
            html.Div(
                f"{period} 最高产量机台",
                style={
                    "color": "#fdfefe",
                    "textAlign": "center",
                    "fontSize": "12px",
                    "lineHeight": "1.2",
                },
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            f"{max_prod_machine}",
                            style={
                                "color": "#2ecc71",
                                "fontSize": "12px",
                                "lineHeight": "1.2",
                            },
                        ),
                        width=6,
                        className="text-start",
                    ),
                    dbc.Col(
                        html.Div(
                            f"{max_prod_value}kg",
                            style={
                                "color": "#3498db",
                                "fontSize": "12px",
                                "lineHeight": "1.2",
                            },
                        ),
                        width=6,
                        className="text-end",
                    ),
                ],
                className="gx-0",
                style={"margin": "0"},
            ),
        ],
        style={
            "backgroundColor": "#202020",
            "height": "auto",
            "padding": "8px 4px",
            "overflow": "hidden",
        },
    )
    card3 = dbc.CardBody(
        [
            html.Div(
                f"{period} 最低产量机台",
                style={
                    "color": "#fdfefe",
                    "textAlign": "center",
                    "fontSize": "12px",
                    "lineHeight": "1.2",
                },
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            f"{min_prod_machine}",
                            style={
                                "color": "#f1c40f",
                                "fontSize": "12px",
                                "lineHeight": "1.2",
                            },
                        ),
                        width=6,
                        className="text-start",
                    ),
                    dbc.Col(
                        html.Div(
                            f"{min_prod_value}kg",
                            style={
                                "color": "#3498db",
                                "fontSize": "12px",
                                "lineHeight": "1.2",
                            },
                        ),
                        width=6,
                        className="text-end",
                    ),
                ],
                className="gx-0",
                style={"margin": "0"},
            ),
        ],
        style={
            "backgroundColor": "#202020",
            "height": "auto",
            "padding": "8px 4px",
            "overflow": "hidden",
        },
    )
    return card1, card2, card3


def create_chart3_figure_detail(
    period: str,
    dfs: Dict[str, Dict[str, pd.DataFrame]],
) -> go.Figure:
    """
    Creates a line chart showing trend over time for 'weight_kg' against 'mmdd' for each machine.

    Args:
        period (str): The key for the period in the dfs dictionary (e.g., "last_7_days").
        dfs (Dict[str, Dict[str, pd.DataFrame]]): A nested dictionary containing DataFrames.
            Expected structure: dfs[period]['all_machine'] should be the target DataFrame.

    Returns:
        go.Figure: A Plotly graph object figure. If data is invalid or missing,
                   an empty figure with an error message/note might be returned.
    """
    fig = go.Figure()  # Initialize an empty figure

    try:
        if (
            not isinstance(dfs, dict)
            or period not in dfs
            or not isinstance(dfs[period], dict)
            or "all_machine" not in dfs[period]
        ):
            raise KeyError(
                f"Expected path dfs[period]['all_machine'] not found or 'dfs' is not structured correctly.\n {type(dfs)=}"
            )
        df_period = dfs[period]
        df = df_period["all_machine"]
    except KeyError as e:
        logger.error(
            f"Data not found for period '{period}' in {dfs.keys()} and key 'all_machine' in {df_period.keys()}. Error: {e}"
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

    if not isinstance(df, pd.DataFrame):
        logger.warning(
            f"Data for period '{period}' and key 'all_machine' is not a DataFrame."
        )
        fig.update_layout(title_text=f"Invalid data format for {period}")
        _make_figure_empty_looking(fig)
        return fig

    if df.empty:
        logger.warning(
            f"DataFrame for period '{period}' and key 'all_machine' is empty."
        )
        fig.update_layout(title_text=f"No data to display for {period}")
        _make_figure_empty_looking(fig)
        return fig

    required_cols = ["mmdd", "weight_kg", "machine_name"]  # Added "machine_name"
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        logger.error(
            f"Missing required columns {missing_cols} in DataFrame for period '{period}'."
        )
        fig.update_layout(title_text=f"Error: Missing data columns for {period}")
        _make_figure_empty_looking(fig)
        return fig

    df_copy = df.copy()
    try:
        df_copy["weight_kg"] = pd.to_numeric(df_copy["weight_kg"], errors="coerce")
        if df_copy["weight_kg"].isnull().all():
            logger.error(
                f"'weight_kg' column for period '{period}' contains no valid numeric data after conversion."
            )
            fig.update_layout(title_text=f"Invalid 'weight_kg' data for {period}")
            _make_figure_empty_looking(fig)
            return fig
        df_copy.dropna(subset=["weight_kg"], inplace=True)
        if df_copy.empty:
            logger.warning(
                f"DataFrame became empty after dropping NaNs in 'weight_kg' for period '{period}'."
            )
            fig.update_layout(title_text=f"No valid 'weight_kg' data for {period}")
            _make_figure_empty_looking(fig)
            return fig

        # Calculate y-axis upper bound for padding based on overall max
        max_y_value = df_copy["weight_kg"].max()
        if pd.notna(max_y_value):
            yaxis_upper_bound = max_y_value * 1.3 if max_y_value > 0 else 10.0
        else:
            yaxis_upper_bound = 10.0

    except Exception as e:
        logger.error(f"Error processing data for period '{period}': {e}")
        fig.update_layout(title_text=f"Error in data processing for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Iterate through each machine and add a trace
    machine_names = df_copy["machine_name"].unique()
    for machine_name in machine_names:
        machine_df = df_copy[df_copy["machine_name"] == machine_name]
        # Sort by mmdd to ensure lines are drawn correctly
        machine_df = machine_df.sort_values(by="mmdd")
        fig.add_trace(
            go.Scatter(
                x=machine_df["mmdd"],
                y=machine_df["weight_kg"],
                mode="lines+markers",  # Removed text
                name=machine_name,  # Use machine_name for legend
                textfont=dict(color="#fdfefe", size=12),
            )
        )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=True,  # Ensure legend is visible
        legend_title_text="Machine",
        legend_font_color="#fdfefe",
        legend_bgcolor="rgba(32,32,32,0.8)",  # Semi-transparent background for legend
        font_color="#fdfefe",
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        xaxis_showline=True,
        yaxis_showline=True,
        xaxis_linecolor="#fdfefe",
        yaxis_linecolor="#fdfefe",
        xaxis_tickfont=dict(color="#fdfefe"),
        yaxis_tickfont=dict(color="#fdfefe"),
        yaxis_range=[0, yaxis_upper_bound],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(type="category"),
    )

    return fig
