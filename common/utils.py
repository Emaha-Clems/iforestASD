import yaml
from pathlib import Path
from typing import Union
import plotly.graph_objects as go



def read_config(path: Union[str, Path]) -> dict:

    """
    Reads a YAML configuration file and returns it as a dictionary.

    Parameters:
    ----------
    path : str or Path
        Path to the YAML file.

    Returns:
    -------
    dict
        Parsed YAML content as a dictionary.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def make_prediction_figures(df_prod, df_labels, features, anomaly_status, end_idx=None):
    
    if end_idx is None:
        end_idx = len(df_prod)
    
    timestamps = df_prod['timestamp_(min)'].copy()
    df_prod_no_ts = df_prod.drop(columns=['timestamp_(min)']).iloc[:end_idx]

    fig = go.Figure()

    #Ground-truth subplot (top) 
    for feat in features:
        fig.add_trace(go.Scatter(
            x=df_prod_no_ts.index,
            y=df_prod_no_ts[feat],
            mode='lines+markers',
            marker=dict(size=6),
            name=f'{feat} value',  
            legendgroup='gt',
            xaxis='x1',
            yaxis='y1'
        ))

        mask = df_labels['timestamp_(min)'].isin(timestamps[:end_idx])
        anomalies = df_labels[mask & (df_labels['label'] == 1)]['timestamp_(min)']
        anomalies_idx = [timestamps[timestamps == ts].index[0] for ts in anomalies]

        if anomalies_idx:
            fig.add_trace(go.Scatter(
                x=anomalies_idx,
                y=df_prod_no_ts.loc[anomalies_idx, feat],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Ground-truth anomaly',  # anomaly points
                legendgroup='gt',
                showlegend=True,
                xaxis='x1',
                yaxis='y1'
            ))

    # iforestASD subplot (bottom) 
    for feat in features:
        fig.add_trace(go.Scatter(
            x=df_prod_no_ts.index,
            y=df_prod_no_ts[feat],
            mode='lines+markers',
            marker=dict(size=6),
            name=f'{feat} value',  
            legendgroup='md',
            xaxis='x2',
            yaxis='y2'
        ))

        detected_anomalies = [
            int(i) for i, status in anomaly_status.items()
            if (status['is_anomaly'] if isinstance(status, dict) else status) and int(i) < end_idx
        ]
        if detected_anomalies:
            fig.add_trace(go.Scatter(
                x=detected_anomalies,
                y=df_prod_no_ts.loc[detected_anomalies, feat],
                mode='markers',
                marker=dict(size=12, color='red'),
                name='Detected anomaly',  # anomaly points
                legendgroup='md',
                showlegend=True,
                xaxis='x2',
                yaxis='y2'
            ))

    fig.update_layout(
        height=700,
        width=900,
        template='plotly_dark',
        plot_bgcolor='#1e2130',
        paper_bgcolor='#1e2130',
        font=dict(color='white', size=12),
        showlegend=True,
 
        xaxis=dict(domain=[0,1], anchor='y1', showgrid=False,  showline=True, linecolor='white'),
        yaxis=dict(domain=[0.55,1], anchor='x1', showgrid=False, title='Value'),
        xaxis2=dict(domain=[0,1], anchor='y2', showgrid=False, showline=True, linecolor='white'),
        yaxis2=dict(domain=[0,0.45], anchor='x2', showgrid=False, title='Value')
    )

   
    fig.update_layout(
        annotations=[
            dict(text="Ground-truth anomalies", x=0.5, y=1.05, xref='paper', yref='paper',
                 showarrow=False, font=dict(size=16, color='white')),
            dict(text="iforestASD detected anomalies", x=0.5, y=0.48, xref='paper', yref='paper',
                 showarrow=False, font=dict(size=16, color='white'))
        ]
    )

    return fig