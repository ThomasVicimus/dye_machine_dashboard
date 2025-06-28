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
        Output("theme-store", "data", allow_duplicate=True),
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

    # NEW: Internal helper to get common styles based on theme
    def _get_common_theme_styles(theme):
        if theme == "black":
            header_style = {
                "backgroundColor": "#2774a7",
                # "fontWeight": "bold",
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
                "textAlign": "center",
                # "textAlign": "left",
                "whiteSpace": "normal",
                "fontFamily": "Microsoft YaHei",
                "width": "auto",
                "padding": "8px",
                "color": "#fdfefe",
            }
        else:  # dark_blue or default
            header_style = {
                "backgroundColor": "#2774a7",
                # "fontWeight": "bold",
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
        return header_style, row_conditional_styling, cell_style

    # NEW: Internal helper for status conditional styling
    def _get_status_conditional_styling(status_column: str | None):
        if not status_column:
            return []
        return [
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

    @app.callback(
        [
            Output("chart-2", "style_header"),
            Output("chart-2", "style_data_conditional"),
            Output("chart-2", "style_cell"),
        ],
        [Input("theme-store", "data"), Input("all-chart-data-store", "data")],
    )
    def update_table_theme(theme, allchart_data):
        header_style, row_conditional_styling, cell_style = _get_common_theme_styles(
            theme
        )

        data = allchart_data["chart-2-data-store"]
        data = deserialize_dataframe_dict(data)
        status_column_name = None  # Renamed for clarity
        df_all_machine = data.get("desktop", None)
        if df_all_machine is not None:
            df = df_all_machine.get("all_machine", None)
            if df is not None:
                column_names = [*df.keys()]
                if len(column_names) > 1:
                    status_column_name = column_names[1]

        status_styles = _get_status_conditional_styling(status_column_name)
        conditional_styling = row_conditional_styling + status_styles

        return header_style, conditional_styling, cell_style

    # Modified helper function for chart 2 detail table styles
    def get_chart2_detail_table_styles(theme: str, status_column: str | None):
        """Get table styling for chart2 detail table based on selected theme and status column."""
        header_style, row_conditional_styling, cell_style = _get_common_theme_styles(
            theme
        )
        status_styles = _get_status_conditional_styling(status_column)
        conditional_styling = row_conditional_styling + status_styles
        return header_style, conditional_styling, cell_style

    # Modified callback to update chart 2 detail table theme
    @app.callback(
        Output("mobile-detail-chart-chart-2-0", "style_header"),
        Output("mobile-detail-chart-chart-2-0", "style_data_conditional"),
        Output("mobile-detail-chart-chart-2-0", "style_cell"),
        Input("theme-store", "data"),
        State(
            "mobile-detail-chart-chart-2-0", "columns"
        ),  # Get columns for status styling
    )
    def callback_update_chart2_detail_theme(theme_store_data, table_columns):
        theme = "black"  # Default theme
        if theme_store_data:
            theme = theme_store_data

        status_col_name = None
        if table_columns and len(table_columns) > 1:
            # Assuming the 'id' of the column object is the column name
            # and the status column is the second one.
            second_column = table_columns[1]
            if isinstance(second_column, dict):
                status_col_name = second_column.get("id")

        return get_chart2_detail_table_styles(theme, status_col_name)
