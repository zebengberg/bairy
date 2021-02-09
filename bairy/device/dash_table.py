"""Create dash table for /table endpoint."""

import os
import pandas as pd
from dash import Dash
from dash.dependencies import Input, Output
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from bairy.device.dash_plot import css
from bairy.device import configs

table = Dash(
    requests_pathname_prefix='/table/',
    external_stylesheets=[css]
)
table.layout = html.Div(children=[
    # title and links
    html.Div(children=[
        html.H1(children='bairy', style={'fontWeight': 'bold'}),
        html.H3(children='Display sensor data from Raspberry Pi.'),
        html.A(
            'about bairy',
            href='https://github.com/zebengberg/bairy',
            style={'margin': '20px'}
        ),
        html.A(
            'plot',
            href='/plot',
            style={'margin': '20px'}
        )
    ]),

    # table
    DataTable(
        id='table',
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender")
    ),

    # for plot update callback
    # see https://dash.plotly.com/live-updates
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0  # an unused counter
    )
])


@table.callback(
    [Output('table', 'columns'), Output('table', 'data')],
    Input('interval-component', 'n_intervals')
)
def serve_table(_):
  """Dynamically serve table columns and data."""

  data_path = configs.PREPROCESSED_DATA_PATHS['day']
  # avoiding errors before any data is captured
  if not os.path.exists(data_path):
    return None, None

  df = pd.read_csv(data_path, index_col=0)
  df = df.iloc[::-1]
  df.index = df.index.astype(str)
  df = df.round(3)
  columns = [{'name': i, 'id': i} for i in df.columns]
  data = df.to_dict('records')
  return columns, data
