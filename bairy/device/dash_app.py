"""Create dash plot and dash table as endpoints."""

from __future__ import annotations
import os
import pandas as pd
import plotly.graph_objects as go
from dash import Dash
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from bairy.device import configs


def determine_plot_configs():
  """Determine plotly axes and variables configurations."""

  d = configs.load_device()
  sensor_headers: dict[str, list[str]] = {'air': [],
                                          'digital': [],
                                          'random': []}
  sensor_units = {'air': 'micrograms / cubic meter',
                  'digital': 'intensity',
                  'random': 'random'}

  for s in d.sensors:
    if s.sensor_type == 'air':
      sensor_headers['air'] += ['pm_1.0', 'pm_2.5', 'pm_1.0']
    else:
      sensor_headers[s.sensor_type].append(s.header)

  # cleanup dictionaries
  empties = [k for k in sensor_headers.keys() if sensor_headers[k] == []]
  for k in empties:
    del sensor_headers[k]
    del sensor_units[k]

  # keeping at most two types of headers
  if len(sensor_headers) == 3:
    del sensor_headers['random']
    del sensor_units['random']

  return sensor_headers, sensor_units


def preprocess_df(time_as_str: bool = False, only_last_day: bool = False):
  """Preprocess pandas DataFrame."""
  df = pd.read_csv(configs.DATA_PATH)

  df = df.set_index('time')
  df.index = pd.to_datetime(df.index)

  sensor_headers, _ = determine_plot_configs()
  cols_to_keep = [col for key in sensor_headers for col in sensor_headers[key]]
  df = df[cols_to_keep]

  if only_last_day:
    start = pd.Timestamp.now() - pd.Timedelta('1 day')
    df = df[df.index > start]

  df = resample_df(df)

  if time_as_str:  # for plotly table
    df = df.iloc[::-1]
    df.index = df.index.astype(str)
  return df.reset_index()  # move time back as a column


def resample_df(df):
  """Smooth and condense df by resampling."""
  rules = ['20S', '30S', '1T', '2T', '4T',
           '5T', '6T', '10T', '20T', '30T', '1H']
  if len(df) < 100:  # no resampling
    return df
  for r in rules:
    df = df.resample(r).mean()
    if len(df) < 5000:
      return df
  return df


def create_fig(only_last_day: bool = False):
  """Create plotly figure using one or two y-axes."""

  fig = go.Figure()
  if not os.path.exists(configs.DATA_PATH) or not os.path.exists(configs.CONFIGS_PATH):
    return fig

  df = preprocess_df(only_last_day=only_last_day)
  sensor_headers, sensor_units = determine_plot_configs()

  # TODO thresholds: 150 for pm10, 35 for pm2.5
  for i, (key, cols) in enumerate(sensor_headers.items()):
    unit = sensor_units[key]
    side = 'left' if i == 0 else 'right'
    yaxis = 'y' if i == 0 else 'y2'
    yaxis_layout = 'yaxis' if i == 0 else 'yaxis2'
    layout_params = {yaxis_layout: {'title': unit, 'side': side}}
    if i == 1:
      layout_params[yaxis_layout]['overlaying'] = 'y'

    for col in cols:
      fig.add_trace(go.Scatter(
          x=df['time'],
          y=df[col],
          name=col,
          yaxis=yaxis))
    fig.update_layout(**layout_params)

  fig.update_layout(height=800)
  return fig


def serve_plot():
  """Dynamically serve dash_plot.layout."""

  fig_day = create_fig(only_last_day=True)
  fig_day.layout.title = 'Data from last 24 hours'
  fig_day.layout.xaxis.rangeslider.visible = True

  fig_all = create_fig(only_last_day=False)
  fig_all.layout.title = 'All available data'
  fig_all.layout.xaxis.rangeslider.visible = True

  return html.Div(children=[

      html.Div(children=[
          html.H1(children='bairy'),
          html.Div(children='Display sensor data from Raspberry Pi.'),
          html.A('about bairy', href='https://github.com/zebengberg/bairy',
                 style={'margin': '20px'}),
          html.A('table', href='/table', style={'margin': '20px'})]),

      dcc.Graph(id='graph_all', figure=fig_all),
      dcc.Graph(id='graph_day', figure=fig_day)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/',
                 external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_plot.layout = serve_plot


def serve_table():
  """Dynamically serve updated dash_table.layout."""
  if not os.path.exists(configs.DATA_PATH) or not os.path.exists(configs.CONFIGS_PATH):
    return DataTable()

  df = preprocess_df(True, True)
  columns = [{'name': i, 'id': i} for i in df.columns]
  data = df.to_dict('records')
  return html.Div(children=[

      html.Div(children=[
          html.H1(children='bairy'),
          html.Div(children='Display sensor data from Raspberry Pi.'),
          html.A('about bairy', href='https://github.com/zebengberg/bairy',
                 style={'margin': '20px'}),
          html.A('plot', href='/plot', style={'margin': '20px'})]),

      DataTable(
          id='table',
          columns=columns,
          data=data,
          style_cell=dict(textAlign='left'),
          style_header=dict(backgroundColor="paleturquoise"),
          style_data=dict(backgroundColor="lavender"))])


dash_table = Dash(requests_pathname_prefix='/table/',
                  external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_table.layout = serve_table
