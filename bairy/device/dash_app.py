"""Create dash plot and dash table as endpoints."""

import os
import pandas as pd
import plotly.graph_objects as go
from dash import Dash
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from bairy.device.configs import DATA_PATH, load_configs


def preprocess_df(time_as_str: bool = False, only_last_day: bool = False):
  """Preprocess pandas DataFrame."""
  if not os.path.exists(DATA_PATH):
    return None
  df = pd.read_csv(DATA_PATH)
  df = df.set_index('time')
  df.index = pd.to_datetime(df.index)

  configs = load_configs()
  cols_to_keep = [col for axis in configs.plot_axes.values() for col in axis]
  df = df[cols_to_keep]
  # thresholds: 150 for pm10, 35 for pm2.5

  if only_last_day:
    start = pd.Timestamp.now() - pd.Timedelta('1 day')
    df = df[df.index > start]
  df = resample_df(df)

  if time_as_str:  # for plotly table
    df = df.iloc[::-1]
    df.index = df.index.astype(str)
  return df.reset_index()  # move time back as a column


def resample_df(df):
  """Modify df by resampling to bound number of points."""
  rules = ['2S', '5S', '10S', '30S', '1T', '2T', '5T', '10T', '30T', '1H']
  for r in rules:
    if len(df) < 5000:
      return df
    df = df.resample(r).mean()
  return df


def create_fig(only_last_day: bool = False):
  """Create plotly figure using one or two y-axes."""

  fig = go.Figure()
  df = preprocess_df(only_last_day=only_last_day)
  if df is None:
    return fig

  units = list(load_configs().plot_axes.keys())
  assert len(units) in [1, 2]

  u = units[0]
  for col in load_configs().plot_axes[u]:
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df[col],
        name=col,
        yaxis='y'))
    fig.update_layout(yaxis={'title': u, 'side': 'left'})

  if len(units) == 2:
    u = units[1]
    for col in load_configs().plot_axes[u]:
      fig.add_trace(go.Scatter(
          x=df['time'],
          y=df[col],
          name=col,
          yaxis='y2'))
      fig.update_layout(
          yaxis2={'title': u, 'side': 'right', 'overlaying': 'y'})

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
  df = preprocess_df(True, True)
  if df is None:
    return DataTable()
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
