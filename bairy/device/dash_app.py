"""Create dash plot and dash table as endpoints."""

from __future__ import annotations
import os
import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from dash import Dash
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from bairy.device import configs


pio.templates.default = 'plotly_white'


def determine_plot_configs():
  """Determine plotly axes and variables configurations."""

  d = configs.load_device()
  # the order of the dictionaries below matter for plot tracing
  # order is least important to most important
  sensor_headers: dict[str, list[str]] = {'random': [],
                                          'digital': [],
                                          'air': []}
  sensor_units = {'random': 'random',
                  'digital': 'intensity',
                  'air': 'micrograms / cubic meter'}

  for s in d.sensors:
    if s.sensor_type == 'air':
      sensor_headers['air'] += ['pm_1.0', 'pm_2.5', 'pm_10']
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


def preprocess_df(time_period: str = 'all', as_str: bool = False):
  """Preprocess pandas DataFrame."""
  df = pd.read_csv(configs.DATA_PATH)

  df = df.set_index('time')
  df.index = pd.to_datetime(df.index)

  sensor_headers, _ = determine_plot_configs()
  cols_to_keep = [col for key in sensor_headers for col in sensor_headers[key]]
  df = df[cols_to_keep]

  if time_period == 'day':
    start = pd.Timestamp.now() - pd.Timedelta('1 day')
    df = df[df.index > start]
  elif time_period == 'week':
    start = pd.Timestamp.now() - pd.Timedelta('7 days')
    df = df[df.index > start]

  df = resample_df(df)

  if as_str:  # for plotly table
    df = df.iloc[::-1]
    df.index = df.index.astype(str)
    df = df.round(3)
  return df.reset_index()  # move time back as a column


def resample_df(df):
  """Smooth and condense df by resampling."""
  # 60 has many divisors
  rules = ['1T', '2T', '3T', '4T', '5T', '6T', '10T', '20T', '30T', '1H']

  if len(df) > 300:  # only resample if df large enough
    for r in rules:
      df = df.resample(r).mean()
      if len(df) < 5000:
        break

  # smoothing even more
  df = df.rolling(7, center=True, min_periods=1).mean()
  return df


def create_fig(time_period: str = 'all'):
  """Create plotly figure using one or two y-axes."""

  # avoiding errors before any data is captured
  if not os.path.exists(configs.DATA_PATH):
    return go.Figure()

  try:
    fig = go.Figure()
    # see https://plotly.com/python/discrete-color/
    colors = iter(px.colors.qualitative.Bold)
    df = preprocess_df(time_period)
    sensor_headers, sensor_units = determine_plot_configs()

    for i, (key, cols) in enumerate(sensor_headers.items()):
      unit = sensor_units[key]
      if len(sensor_headers) == 2 and i == 0:
        side = 'right'
        opacity = 0.4
      else:
        side = 'left'
        opacity = 1.0

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
            opacity=opacity,
            line={'color': next(colors)},
            yaxis=yaxis))
      fig.update_layout(**layout_params)

    # threshold for pm2.5
    if 'air' in sensor_headers and df['pm_2.5'].max() > 40:
      yaxis = 'y2' if len(sensor_headers) == 2 else 'y'
      fig.add_trace(go.Scatter(
          x=df['time'],
          y=[35] * len(df),
          name='pm_2.5 safe threshold',
          yaxis=yaxis,
          line={'dash': 'dot', 'color': next(colors)}))

    name = configs.load_device().name
    if time_period == 'day':
      title = f'{name} data over last 24 hours'
    elif time_period == 'week':
      title = f'{name} data over last 7 days'
    else:
      title = f'{name} data over entire runtime'

    fig.update_layout(height=800, title=title)
    fig.layout.xaxis.rangeslider.visible = True
    fig.layout.yaxis.fixedrange = False
    return fig

  except (KeyError, FileNotFoundError) as e:
    logging.info(e)
    return go.Figure()


def serve_plot():
  """Dynamically serve dash_plot.layout."""

  fig_day = create_fig('day')
  fig_week = create_fig('week')
  fig_all = create_fig()

  return html.Div(children=[
      html.Div(children=[
          html.H1(children='bairy', style={'fontWeight': 'bold'}),
          html.H3(children='Display sensor data from Raspberry Pi.'),
          html.A(
              'about bairy',
              href='https://github.com/zebengberg/bairy',
              style={'margin': '20px'}),
          html.A(
              'table',
              href='/table',
              style={'margin': '20px'})]),
      dcc.Graph(id='graph_day', figure=fig_day),
      dcc.Graph(id='graph_week', figure=fig_week),
      dcc.Graph(id='graph_all', figure=fig_all)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_plot.layout = serve_plot


def serve_table():
  """Dynamically serve updated dash_table.layout."""

  # avoiding errors before any data is captured
  if not os.path.exists(configs.DATA_PATH):
    return DataTable()

  try:
    df = preprocess_df('day', True)
    columns = [{'name': i, 'id': i} for i in df.columns]
    data = df.to_dict('records')
    table = DataTable(
        id='table',
        columns=columns,
        data=data,
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"))

  except (KeyError, FileNotFoundError) as e:
    logging.info(e)
    table = DataTable()

  return html.Div(children=[
      html.Div(children=[
          html.H1(children='bairy', style={'fontWeight': 'bold'}),
          html.H3(children='Display sensor data from Raspberry Pi.'),
          html.A(
              'about bairy',
              href='https://github.com/zebengberg/bairy',
              style={'margin': '20px'}),
          html.A(
              'plot',
              href='/plot',
              style={'margin': '20px'})]),
      table])


dash_table = Dash(requests_pathname_prefix='/table/',
                  external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_table.layout = serve_table
