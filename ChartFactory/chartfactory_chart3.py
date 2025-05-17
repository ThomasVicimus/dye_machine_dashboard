import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Optional
import logging

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
        yaxis_upper_bound = (
            max_y_value * 1.2 if max_y_value > 0 else 10
        )  # Add 20% padding, handle case of all zeros

    except Exception as e:
        logger.error(
            f"Error converting 'weight_kg' to numeric for period '{period}': {e}"
        )
        fig.update_layout(title_text=f"Error in 'weight_kg' data for {period}")
        _make_figure_empty_looking(fig)
        return fig

    fig.add_trace(
        go.Scatter(
            x=df_copy["mmdd"],
            y=df_copy["weight_kg"],
            mode="lines+markers+text",
            text=df_copy["weight_kg"],
            textposition="top right",
            textfont=dict(size=12),
        )
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        font_color="#fdfefe",  # General text color
        margin=dict(l=30, r=30, t=40, b=20),
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
