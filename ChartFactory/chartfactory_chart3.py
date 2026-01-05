import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, List
import logging
from dash import html
import dash_bootstrap_components as dbc
import math

from function.text_utilities import truncate_title


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

    required_cols = ["date", "weight_kg", "order_index"]
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        logger.error(
            f"Missing required columns {missing_cols} in DataFrame for period '{period}'."
        )
        fig.update_layout(title_text=f"Error: Missing data columns for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Filter to only use order_index == 0 (averages/totals)
    df_copy = df[df["order_index"] == 0].copy()

    if df_copy.empty:
        logger.warning(f"No data with order_index == 0 found for period '{period}'.")
        fig.update_layout(title_text=f"No average data available for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Convert date to mmdd format for x-axis display
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    if "mmdd" not in df_copy.columns:
        df_copy["mmdd"] = df_copy["date"].dt.strftime("%m-%d")

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

        # Calculate y-axis upper bound for padding
        max_y_value = df_copy["weight_kg"].max()
        if pd.notna(max_y_value):
            yaxis_upper_bound = max_y_value * 1.3 if max_y_value > 0 else 10.0
        else:
            yaxis_upper_bound = 10.0

    except Exception as e:
        logger.error(
            f"Error converting 'weight_kg' to numeric for period '{period}': {e}"
        )
        fig.update_layout(title_text=f"Error in 'weight_kg' data for {period}")
        _make_figure_empty_looking(fig)
        return fig

    # Since data is pre-processed to always have exactly 7 data points, show all values
    text_values = df_copy["weight_kg"].tolist() if not df_copy.empty else []

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
    # Filter to only use order_index == 0 (averages/totals)
    card1_mask = (df.period == period) & (df.order_index == 0)
    card2_3_mask = (df.period == period) & (df.order_index == 1)
    # * Card1
    df_card1 = df.loc[card1_mask]
    if df_card1.empty:
        total_prod = 0
    else:
        total_prod = df_card1["weight_kg"].sum()
    df_card2_3 = df.loc[card2_3_mask]
    if df_card2_3.empty:
        max_prod_machine = "N/A"
        max_prod_value = 0
        min_prod_machine = "N/A"
        min_prod_value = 0
    else:
        # * Card2
        max_prod_machine = df_card2_3.loc[
            df_card2_3["weight_kg"].idxmax(), "machine_name"
        ]
        max_prod_value = df_card2_3["weight_kg"].max()
        # * Card3
        min_prod_machine = df_card2_3.loc[
            df_card2_3["weight_kg"].idxmin(), "machine_name"
        ]
        min_prod_value = df_card2_3["weight_kg"].min()

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
                f"{period} 最高产量",
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
                f"{period} 最低产量",
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
) -> List[go.Figure]:
    """
    Creates a list of figures for the detail view.

    - output_figures[0]: Overall (order_index == 0) trend figure (overview)
    - output_figures[1...N]: Per-machine figures, 3 machines per figure (1x3 subplots)

    Args:
        period (str): The key for the period in the dfs dictionary (e.g., "last_7_days").
        dfs (Dict[str, Dict[str, pd.DataFrame]]): A nested dictionary containing DataFrames.
            Expected structure: dfs[period]['all_machine'] should be the target DataFrame.

    Returns:
        List[go.Figure]: A list of Plotly figures suitable for the mobile detail page.
    """
    output_figures: List[go.Figure] = []

    # First figure: reuse the existing "overview" builder for consistency
    try:
        fig_overview = create_chart3_figure(period, dfs)
        fig_overview.update_layout(
            title_text="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
        )
        output_figures.append(fig_overview)
    except Exception as e:
        logger.error(f"Error creating chart3 overview figure for '{period}': {e}")
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"Error: {e}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]

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
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"Data not available for {period}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]
    except TypeError as e:
        logger.error(
            f"Invalid structure for 'dfs' argument for period '{period}'. Expected Dict[str, Dict[str, pd.DataFrame]]. Error: {e}"
        )
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"Invalid data structure for {period}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]

    if not isinstance(df, pd.DataFrame):
        logger.warning(
            f"Data for period '{period}' and key 'all_machine' is not a DataFrame."
        )
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"Invalid data format for {period}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]

    if df.empty:
        logger.warning(
            f"DataFrame for period '{period}' and key 'all_machine' is empty."
        )
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"No data to display for {period}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]

    required_cols = ["date", "weight_kg", "machine_name", "order_index"]
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        logger.error(
            f"Missing required columns {missing_cols} in DataFrame for period '{period}'."
        )
        fig_err = go.Figure()
        fig_err.update_layout(title_text=f"Error: Missing data columns for {period}")
        _make_figure_empty_looking(fig_err)
        return [fig_err]

    # Filter to only use order_index == 1 (individual machines)
    df_copy = df[df["order_index"] == 1].copy()

    if df_copy.empty:
        logger.warning(
            f"No individual machine data (order_index == 1) found for period '{period}'."
        )
        # Return overview only (already in output_figures)
        return output_figures

    # Convert date to mmdd format for x-axis display
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy["mmdd"] = df_copy["date"].dt.strftime("%m-%d")
    try:
        df_copy["weight_kg"] = pd.to_numeric(df_copy["weight_kg"], errors="coerce")
        if df_copy["weight_kg"].isnull().all():
            logger.error(
                f"'weight_kg' column for period '{period}' contains no valid numeric data after conversion."
            )
            return output_figures
        df_copy.dropna(subset=["weight_kg"], inplace=True)
        if df_copy.empty:
            logger.warning(
                f"DataFrame became empty after dropping NaNs in 'weight_kg' for period '{period}'."
            )
            return output_figures

    except Exception as e:
        logger.error(f"Error processing data for period '{period}': {e}")
        return output_figures

    # Build per-machine subplots: 3 machines per figure
    machine_names = sorted(df_copy["machine_name"].dropna().unique().tolist())
    if not machine_names:
        return output_figures

    machines_per_fig = 3
    num_figs = math.ceil(len(machine_names) / machines_per_fig)

    for fig_idx in range(num_figs):
        start = fig_idx * machines_per_fig
        end = min((fig_idx + 1) * machines_per_fig, len(machine_names))
        chunk_names = machine_names[start:end]

        subplot_titles = [truncate_title(n, max_len=18) for n in chunk_names]
        # pad to 3 columns for consistent layout
        while len(subplot_titles) < machines_per_fig:
            subplot_titles.append("")

        fig_row = make_subplots(
            rows=1,
            cols=machines_per_fig,
            subplot_titles=subplot_titles,
            horizontal_spacing=0.04,
        )

        max_y_chunk = 0.0
        for j, machine_name in enumerate(chunk_names):
            mdf = df_copy[df_copy["machine_name"] == machine_name].sort_values("date")
            if mdf.empty:
                continue
            max_y_chunk = max(max_y_chunk, float(mdf["weight_kg"].max()))
            text_values = mdf["weight_kg"].tolist()
            fig_row.add_trace(
                go.Scatter(
                    x=mdf["mmdd"],
                    y=mdf["weight_kg"],
                    mode="lines+markers+text",
                    text=text_values,
                    textposition="top right",
                    textfont=dict(color="#fdfefe", size=12),
                    showlegend=False,
                    line=dict(width=2),
                    marker=dict(size=6),
                ),
                row=1,
                col=j + 1,
            )

        y_upper = max_y_chunk * 1.3 if max_y_chunk > 0 else 10.0

        fig_row.update_layout(
            title_text="",
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#fdfefe",
            autosize=True,
        )
        fig_row.update_annotations(font=dict(size=12, color="#fdfefe"))

        for c in range(1, machines_per_fig + 1):
            fig_row.update_xaxes(
                row=1,
                col=c,
                showgrid=False,
                showline=True,
                linecolor="#fdfefe",
                tickfont=dict(color="#fdfefe", size=10),
                type="category",
            )
            fig_row.update_yaxes(
                row=1,
                col=c,
                showgrid=False,
                showline=True,
                linecolor="#fdfefe",
                tickfont=dict(color="#fdfefe", size=10),
                range=[0, y_upper],
            )

        output_figures.append(fig_row)

    return output_figures
