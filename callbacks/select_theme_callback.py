from dash import html, dcc, Output, Input, State, callback_context, ALL
import logging
from Database.serialize_df import deserialize_dataframe_dict

logger = logging.getLogger(__name__)


def register_theme_callbacks(
    app, default_color: str = "black", default_lang: str = "zh_cn"
):

    COLOR_THEMES = {
        "dark_blue": {
            "background": "#061023",
            "text": "#fdfefe",
            "card": "#16213e",
            "border": "#3c3c3c",
        },
        "black": {
            "background": "#202020",
            "text": "#fdfefe",
            "card": "#1a1a1a",
            "border": "#3c3c3c",
        },
        # "white": {
        #     "background": "#fdfefe",
        #     "text": "#000000",
        #     "card": "#f0f0f0",
        #     "border": "#3c3c3c",
        # },
    }

    # Add callback for theme buttons
    @app.callback(
        Output("theme-store", "data"),
        Input({"type": "theme-button", "index": ALL}, "n_clicks"),
        State("theme-store", "data"),
        prevent_initial_call=True,
    )
    def update_theme(n_clicks, current_theme):
        # Get the triggered button
        ctx = callback_context
        if not ctx.triggered:
            return current_theme

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            # Extract the theme (index) from the button ID
            selected_theme = eval(button_id)["index"]
            if selected_theme in COLOR_THEMES:
                logger.info(f"Theme changed to: {selected_theme}")
                return selected_theme
        except:
            pass

        return current_theme

    @app.callback(
        Output("dashboard-content", "style"),
        Input("theme-store", "data"),
    )
    def apply_theme(theme):
        theme_colors = COLOR_THEMES[theme]
        content_style = {
            "backgroundColor": theme_colors["background"],
            "color": theme_colors["text"],
            "width": "100vw",
            "height": "100vh",
            "overflowY": "auto",
            "position": "relative",
        }
        logger.info(
            f"Applying theme: {theme}, background: {theme_colors['background']}"
        )
        return content_style

    @app.callback(
        [
            Output("chart-2", "style_header"),
            Output("chart-2", "style_data_conditional"),
            Output("chart-2", "style_cell"),
        ],
        [Input("theme-store", "data"), Input("all-chart-data-store", "data")],
    )
    def update_table_theme(theme, allchart_data):
        # get column name
        data = allchart_data["chart-2-data-store"]
        data = deserialize_dataframe_dict(data)
        status_column = ""
        df = data.get("desktop", None)
        column_names = [*df.keys()]
        status_column = column_names[1] if len(column_names) > 1 else None

        """Update table styling based on selected theme."""
        if theme == "black":
            header_style = {
                "backgroundColor": "#999999",
                "fontWeight": "bold",
                "color": "#ffffff",
            }
            row_conditional_styling = [
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#202020",
                },
                {
                    "if": {"row_index": "even"},
                    "backgroundColor": "#464646",
                },
            ]
            cell_style = {
                "textAlign": "left",
                "padding": "8px",
                "color": "#fdfefe",
            }
        else:  # dark_blue
            header_style = {
                "backgroundColor": "#16213e",
                "fontWeight": "bold",
                "color": "#ffffff",
            }
            row_conditional_styling = [
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#061023",
                },
                {
                    "if": {"row_index": "even"},
                    "backgroundColor": "#0c2149",
                },
            ]
            cell_style = {
                "textAlign": "left",
                "padding": "8px",
                "color": "#fdfefe",
            }

        # Add machine status conditional formatting
        # This assumes the second column contains machine status
        status_conditional_styling = [
            # Running - Green
            {
                "if": {
                    "column_id": status_column,
                    "filter_query": f'{{{status_column}}} eq "行機" or {{{status_column}}} eq "行机"',
                },
                "backgroundColor": "#2ecc71",  # Green
                "color": "white",
            },
            # Paused - Yellow
            {
                "if": {
                    "column_id": status_column,
                    "filter_query": f'{{{status_column}}} eq "暫停" or {{{status_column}}} eq "暂停"',
                },
                "backgroundColor": "#f1c40f",  # Yellow-orange
                "color": "black",
            },
            # Stopped - Red
            {
                "if": {
                    "column_id": status_column,
                    "filter_query": f'{{{status_column}}} eq "停機" or {{{status_column}}} eq "停机"',
                },
                "backgroundColor": "#e74c3c",  # Red
                "color": "white",
            },
        ]

        # Combine row styling with status styling
        conditional_styling = row_conditional_styling + status_conditional_styling

        return header_style, conditional_styling, cell_style
