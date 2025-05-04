import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from chart_factory_MachineUasge import MachineUsageChart
import pandas as pd

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for demonstration (this will be replaced with real data later)
sample_data = {
    "machine_usage": {
        "2024-01": {
            "avg": pd.DataFrame(
                {"run": [60], "idle": [20], "down": [10], "repair": [10]}
            ),
            "best": pd.DataFrame(
                {
                    "run": [80],
                    "idle": [10],
                    "down": [5],
                    "repair": [5],
                    "machine_name": ["Best Machine"],
                }
            ),
            "worst": pd.DataFrame(
                {
                    "run": [40],
                    "idle": [30],
                    "down": [20],
                    "repair": [10],
                    "machine_name": ["Worst Machine"],
                }
            ),
        }
    }
}

# Create chart factory instance
chart_factory = MachineUsageChart(sample_data, lang="zh_cn")

# Create a single chart for demonstration
chart = chart_factory.create_machine_usage_chart(
    "2024-01",
    sample_data["machine_usage"]["2024-01"]["avg"],
    sample_data["machine_usage"]["2024-01"]["best"],
    sample_data["machine_usage"]["2024-01"]["worst"],
)

# Define the layout
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            [
                dbc.Col(
                    html.H1("Dye Machine Dashboard", className="text-center my-3"),
                    width=12,
                )
            ]
        ),
        # First row of charts
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-1")], width=4, className="p-2"
                ),
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-2")], width=4, className="p-2"
                ),
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-3")], width=4, className="p-2"
                ),
            ],
            className="mb-2",
        ),
        # Second row of charts
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-4")], width=4, className="p-2"
                ),
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-5")], width=4, className="p-2"
                ),
                dbc.Col(
                    [dcc.Graph(figure=chart, id="chart-6")], width=4, className="p-2"
                ),
            ]
        ),
    ],
    fluid=True,
    style={"max-width": "1920px", "padding": "20px"},
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
