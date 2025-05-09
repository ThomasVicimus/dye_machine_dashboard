from dash import html, dcc, Output, Input, State, callback_context, ALL
import logging

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
        Input("theme-store", "data"),
    )
    def update_table_theme(theme):
        """Update table styling based on selected theme."""
        if theme == "black":
            header_style = {
                "backgroundColor": "#999999",
                "fontWeight": "bold",
                "color": "#ffffff",
            }
            conditional_styling = [
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
            conditional_styling = [
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

        return header_style, conditional_styling, cell_style
