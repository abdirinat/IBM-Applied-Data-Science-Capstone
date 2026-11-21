"""IBM SpaceX Capstone — completed Plotly Dash lab.

Put spacex_launch_dash.csv in the same folder and run:
    pip install dash pandas plotly
    python spacex_dash_app_completed.py
"""
from pathlib import Path

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

DATA_PATH = Path(__file__).with_name('spacex_launch_dash.csv')
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f'Missing {DATA_PATH.name}. Download the IBM lab dataset and place it next to this script: '
        'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
        'IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv'
    )
spacex_df = pd.read_csv(DATA_PATH)
spacex_df['class'] = pd.to_numeric(spacex_df['class'], errors='raise').astype(int)
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
min_payload = float(spacex_df['Payload Mass (kg)'].min())
max_payload = float(spacex_df['Payload Mass (kg)'].max())
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': str(s), 'value': str(s)} for s in sorted(spacex_df['Launch Site'].dropna().unique())
]

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),
    dcc.Dropdown(id='site-dropdown', options=site_options, value='ALL',
                 placeholder='Select a Launch Site here', searchable=True),
    dcc.Graph(id='success-pie-chart'),
    html.P('Payload range (kg):'),
    dcc.RangeSlider(id='payload-slider', min=0,
                    max=max(10000, int(max_payload) + 1000), step=1000,
                    value=[min_payload, max_payload],
                    marks={0: '0', int(max(10000, max_payload)): f'{int(max(10000, max_payload)):,}'}),
    dcc.Graph(id='success-payload-scatter-chart'),
], style={'maxWidth': '1100px', 'margin': 'auto', 'padding': '20px'})

@app.callback(Output('success-pie-chart', 'figure'), Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        successes = spacex_df[spacex_df['class'] == 1]
        counts = successes.groupby('Launch Site').size().reset_index(name='Successful launches')
        return px.pie(counts, values='Successful launches', names='Launch Site',
                      title='Successful Falcon 9 Landings by Launch Site')
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    counts = filtered_df['class'].map({0: 'Failed', 1: 'Successful'}).value_counts().rename_axis('Outcome').reset_index(name='Count')
    return px.pie(counts, values='Count', names='Outcome',
                  title=f'Landing Outcomes at {entered_site}')

@app.callback(Output('success-payload-scatter-chart', 'figure'),
              Input('site-dropdown', 'value'), Input('payload-slider', 'value'))
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    if payload_range:
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'].between(*payload_range)]
    return px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                      color='Booster Version Category',
                      hover_data=['Launch Site'],
                      title='Payload Mass vs. Landing Outcome (1 = Success, 0 = Failure)')

if __name__ == '__main__':
    app.run(debug=False)
