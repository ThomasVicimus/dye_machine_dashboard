    create_chart6_figure,
    create_chart6_txt_cards,
    create_chart6_figure_mobile,
    create_chart6_txt_cards_mobile_main,
)
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc
import logging
from dash import html

logger = logging.getLogger(__name__)

from function.dash_graph_config import NON_INTERACTIVE_GRAPH_CONFIG

def create_chart6_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-6",
    mobile: bool = False,
):
    """Creates the layout with card1 in column 1 and combined_cards+figure in column 2."""

    # Get the cards and configure layout based on mode
    if mobile:
        # Use mobile factory (returns 2 cards)
        card1, card2 = create_chart6_txt_cards_mobile_main(default_period, dfs)
        card3 = None
        
        # Mobile combined cards: Only Card 2
        card2 = dbc.Card(
            getattr(card2, "children", card2),
            id="chart6-card-2",
            style={"height": "auto", "overflow": "hidden"},
        )
        combined_cards = dbc.Row(
            [dbc.Col(card2, width=12)],
            className="mb-2 g-2",
            style={"height": "auto"},
        )
    else:
        # Desktop factory (returns 3 cards)
        card1, card2, card3 = create_chart6_txt_cards(default_period, dfs)
        
        # Ensure Chart-6 text cards have stable IDs in the layout.
        card2 = dbc.Card(
            getattr(card2, "children", card2),
            id="chart6-card-2",
            style={"height": "auto", "overflow": "hidden"},
        )
        card3 = dbc.Card(
            getattr(card3, "children", card3),
            id="chart6-card-3",
            style={"height": "auto", "overflow": "hidden"},
        )

        # Create combined cards for layout compatibility
        combined_cards = dbc.Row(
            [
                dbc.Col(card3, width=6),
                dbc.Col(card2, width=6),
            ],
            className="mb-2 g-2",
            style={"height": "auto"},
        )

    # *Desktop Chart
    if not mobile:
        initial_figure = create_chart6_figure(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=10, b=80),  # More bottom margin for legend
            # Move legend to bottom
            legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.2,  # Position below the plot
                xanchor="center",
                x=0.5,
                font=dict(color="#fdfefe"),
            ),
        )

        # Create the combined right side (cards + figure)
        combined_fig = html.Div(
            [
                # Row 1: Combined cards
                html.Div(
                    combined_cards,
                    style={"marginBottom": "10px"},
                ),
                # Row 2: Figure (responsive)
                html.Div(
                    dcc.Graph(
                        id=chart_id,
                        figure=initial_figure,
                        config=NON_INTERACTIVE_GRAPH_CONFIG,
                        style={"width": "100%", "height": "100%"},
                    ),
                    style={"height": "calc(100% - 80px)", "minHeight": "240px"},
                ),
            ],
            style={"height": "100%"},
        )

        # Create the main 2-column layout
        return dbc.Row(
            [
                # Column 1: Large card1
                dbc.Col(
                    dbc.Card(
                        card1,
                        id="chart6-card-1",
                        className="h-100",
                    ),
                    width=4,
                    style={"height": "100%"},
                ),
                # Column 2: Combined cards + figure
                dbc.Col(
                    combined_fig,
                    width=8,
                    style={"height": "100%"},
                ),
            ],
            className="h-100 g-2",
            style={"height": "100%"},
        )
    else:
        # *Mobile Chart
        initial_figure = create_chart6_figure_mobile(
            default_period,
            dfs,
        )
        initial_figure.update_layout(
            autosize=True,
            height=None,
            margin=dict(l=10, r=10, t=10, b=80),  # More bottom margin for legend
            # Move legend to bottom
            legend=dict(
                orientation="h",  # Horizontal orientation
                yanchor="top",
                y=-0.2,  # Position below the plot
                xanchor="center",
                x=0.5,
                font=dict(color="#fdfefe"),
            ),
        )

        # Combined cards (Top right)
        # We assume combined_cards is defined above (Rows with Cols).
        # We'll just wrap it in a div that doesn't force a height, allowing it to take natural size.
        cards_section = html.Div(
                    combined_cards,
                    style={"marginBottom": "10px"},
        )
        
        # Graph section (Bottom right)
        # Use dcc.Graph with responsive config
        graph_section = html.Div(
                    dcc.Graph(
                        id=chart_id,
                        figure=initial_figure,
                config=NON_INTERACTIVE_GRAPH_CONFIG,
                        style={"width": "100%", "height": "100%"},
                    ),
            className="chart6-graph-wrap",
        )

        # Right column: Flex column with Cards (fixed) + Graph (grow)
        right_col = html.Div(
            [
                cards_section,
                graph_section,
            ],
            className="chart6-right",
        )

        # Left column: Card 1 (fixed width)
        left_col = html.Div(
                    dbc.Card(
                        card1,
                        id="chart6-card-1",
                        className="h-100",
                    ),
            className="chart6-left",
        )

        # Main Layout: Flex Row
        mobile_layout = html.Div(
            [
                left_col,
                right_col,
            ],
            className="chart6-tile",
        )

        return dcc.Link(
            mobile_layout,
            href=f"/details/{chart_id}",  # Link using the chart ID
            id=f"link-{chart_id}",
            style={
                "display": "block",
                "height": "100%",
                "width": "100%",
                "textDecoration": "none", # Remove link underline if any
                "color": "inherit" # Inherit text color
            },
        )


def create_chart6_txtcards_layout(period, dfs):
    """
    Creates a simple 3-column layout for basic display:
    - Column 1: Large card1 (overall statistics)
    - Columns 2-3: Combined cards (card2 + card3) side by side
    """
    card1, card2, card3 = create_chart6_txt_cards(period, dfs)
    
    # Ensure Chart-6 text cards have stable IDs in the layout.
    card2 = dbc.Card(
        getattr(card2, "children", card2),
        id="chart6-card-2",
        style={"height": "auto", "overflow": "hidden"},
    )
    card3 = dbc.Card(
        getattr(card3, "children", card3),
        id="chart6-card-3",
        style={"height": "auto", "overflow": "hidden"},
    )

    # Create combined cards for layout compatibility
    combined_cards = dbc.Row(
        [
            dbc.Col(card3, width=6),
            dbc.Col(card2, width=6),
        ],
        className="mb-2 g-2",
        style={"height": "auto"},
    )

    # Create the layout
    cards_row = dbc.Row(
        [
            # Column 1: Large card spanning one column
            dbc.Col(
                dbc.Card(
                    card1,
                    id="chart6-card-1",  # Unique ID for callbacks
                    className="h-100",
                ),
                width=4,
            ),
            # Columns 2-3: Combined cards
            dbc.Col(
                html.Div(
                    combined_cards,
                    id="chart6-combined-cards",
                ),
                width=8,
            ),
        ],
        className="mb-0 g-2 mt-n3 mx-n3",
        style={"height": "30%"},  # Cards take 30% of the container height
    )
    return cards_row


def create_chart6_detailed_layout(
    default_period: str,
    dfs: dict,
    chart_id: str = "chart-6-detail",
    mobile: bool = False,
):
    """
    Creates a detailed layout with 2-column structure:
    - Column 1: Large card1 (overall statistics) spanning full height
    - Column 2: Row 1 - combined cards (card2 + card3), Row 2 - main figure
    """
    card1, card2, card3 = create_chart6_txt_cards(default_period, dfs)

    # Ensure Chart-6 text cards have stable IDs in the layout.
    card2 = dbc.Card(
        getattr(card2, "children", card2),
        id="chart6-card-2",
        style={"height": "auto", "overflow": "hidden"},
    )
    card3 = dbc.Card(
        getattr(card3, "children", card3),
        id="chart6-card-3",
        style={"height": "auto", "overflow": "hidden"},
    )

    # Create combined cards for layout compatibility
    combined_cards = dbc.Row(
        [
            dbc.Col(card3, width=6),
            dbc.Col(card2, width=6),
        ],
        className="mb-2 g-2",
        style={"height": "auto"},
    )

    # Create the main figure with 2 subplots
    main_figure = create_chart6_figure(default_period, dfs)
    main_figure.update_layout(
        autosize=True,
        height=None,
        margin=dict(l=5, r=5, t=5, b=5),
    )

    # Create the combined element with cards and figure
    combined_right_side = html.Div(
        [
            # Row 1: Combined cards
            html.Div(
                combined_cards,
                style={"marginBottom": "10px"},
            ),
            # Row 2: Main figure
            html.Div(
                dcc.Graph(
                    id=f"{chart_id}-main",
                    figure=main_figure,
                    config=NON_INTERACTIVE_GRAPH_CONFIG,
                    style={"height": "100%", "width": "100%"},
                ),
                style={"height": "calc(100% - 80px)", "minHeight": "200px"},
            ),
        ],
        style={"height": "300px"},
    )

    detailed_layout = dbc.Row(
        [
            # Column 1: Large card spanning full height
            dbc.Col(
                dbc.Card(
                    card1,
                    id="chart6-detail-card-1",
                    className="h-100",
                ),
                width=4,
                style={"height": "300px"},
            ),
            # Column 2: Combined cards + figure
            dbc.Col(
                combined_right_side,
                width=8,
                style={"height": "300px"},
            ),
        ],
        className="mb-0 g-2",
        style={"height": "300px"},
    )

    return detailed_layout
