import os
import sys
from pathlib import Path
import requests
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, 'app-ml', 'src'))
os.chdir(project_root)

from common.data_manager import DataManager
from common.utils import read_config, make_prediction_figures

# Configuration 
config_path = project_root / 'config' / 'config.yaml'
config = read_config(config_path)


# Override host for Docker environment if environment variable is set
inference_api_host = os.environ.get('INFERENCE_API_HOST', config.get('inference_api', {}).get('host', 'localhost'))
inference_api_port = config.get('inference_api', {}).get('port', 5001)
inference_api_endpoint = config.get('inference_api', {}).get('endpoint', '/run-inference')
INFERENCE_API_URL = f"http://{inference_api_host}:{inference_api_port}{inference_api_endpoint}"

# Inference API endpoint
#INFERENCE_API_URL = f"http://{config['inference_api']['host']}:{config['inference_api']['port']}{config['inference_api']['endpoint']}"

# Initialize data manager
data_manager = DataManager(config)
data_manager.initialize_prod_database()

# Dash App 
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Colors
PRIMARY_BG = "#161a28"
CARD_BG = "#1e2130"
TEXT_COLOR = "#ffffff"

app.layout = dbc.Container([
    dcc.Store(id='inference-trigger', data=0),

    dbc.Row([
        dbc.Col([], width=3),  
        dbc.Col([
            dbc.Row([
                dbc.Col(
                    dcc.Graph(id='combined-fig', style={"backgroundColor": PRIMARY_BG}),
                    width=8
                ),
                dbc.Col(
                    dbc.Card([
                        html.H4("Control Panel", style={"color": TEXT_COLOR, "marginBottom": "20px"}),
                        html.Label("Select Feature", style={"color": TEXT_COLOR}),
                        dcc.Dropdown(
                            id='feature-dropdown',
                            options=[{'label': c, 'value': c} for c in data_manager.prod_df.columns if c != 'stream_index'],
                            value=data_manager.prod_df.columns[1],
                            clearable=False,
                            style={"color": "#000000"}
                        ),
                        html.Br(),
                        dbc.Button("Next point", id='next-point-btn', n_clicks=0, color="primary", style={"marginTop": "10px"}),
                        html.Br(), html.Br(),
                        dbc.Checklist(
                            options=[{"label": "Auto-run", "value": 1}],
                            id="auto-run-checklist",
                            inline=True,
                            style={"color": TEXT_COLOR}
                        )
                    ], body=True, style={"backgroundColor": CARD_BG, "padding": "20px", "borderRadius": "5px"})
                , width=4)
            ])
        ], width=11)
    ]),

    dcc.Interval(
        id='interval-component',
        interval=500,  
        n_intervals=0,
        disabled=True
    )
], fluid=True, style={"backgroundColor": PRIMARY_BG, "padding": "20px"})

# Callbacks
@app.callback(
    Output('interval-component', 'disabled'),
    Input('auto-run-checklist', 'value')
)
def toggle_auto_run(val):
    return False if val and 1 in val else True

@app.callback(
    Output('inference-trigger', 'data'),
    Input('next-point-btn', 'n_clicks'),
    Input('interval-component', 'n_intervals')
)
def trigger_inference(n_clicks, n_intervals):
    idx = data_manager.current_stream_index
    if idx >= len(data_manager.prod_df):
        return dash.no_update
    try:
        response = requests.post(INFERENCE_API_URL)
        if response.status_code == 200:
            result = response.json()
            data_manager.anomaly_status = result["anomaly_status"]
            data_manager.current_stream_index += 1
        else:
            print(f"Inference API error: {response.text}")
    except Exception as e:
        print(f"Inference request failed: {e}")
    return idx

@app.callback(
    Output('combined-fig','figure'),
    Input('inference-trigger','data'),
    State('feature-dropdown','value')
)
def update_plot(trigger_idx, feature):
    if trigger_idx is None or trigger_idx >= len(data_manager.prod_df):
        return dash.no_update

    df_labels = data_manager.load_label_data()
    fig = make_prediction_figures(
        data_manager.prod_df, df_labels, [feature],
        data_manager.anomaly_status, end_idx=trigger_idx+1
    )
    return fig

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
