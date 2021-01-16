"""Dash app to plot device data."""

import os
import glob
import pandas as pd
import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from bairy.hub.configs import DATA_DIR, load_ips
from bairy.device.configs import DATA_DIR as DEVICE_DATA_DIR
from bairy.device.dash_app import resample_df


def load_data():
  """Load cached data."""
  ip_addresses = load_ips()
  dfs = glob.glob(DATA_DIR + '/*.csv')
  if 'self' in ip_addresses:
    dfs.append(os.path.join(DEVICE_DATA_DIR, 'data.csv'))
  if dfs == []:
    return None

  dfs = [pd.read_csv(f) for f in dfs]
  dfs = [df[['time', 'pm_2.5']] for df in dfs]
  dfs = [df.set_index(pd.to_datetime(df['time'])) for df in dfs]
  dfs = [df.drop('time', axis=1) for df in dfs]
  # TODO: give better name
  dfs = [df.rename(columns={'pm_2.5': i}) for i, df in enumerate(dfs)]

  df = pd.concat(dfs)
  # start = pd.Timestamp.now() - pd.Timedelta('1 day')
  # df = df[df.index > start]
  df = resample_df(df)
  return df


def create_fig():
  """Create plotly figure using one or two y-axes."""
  df = load_data()
  if df is None:
    return px.line()
  fig = px.line(df, x=df.index, y=df.columns)
  fig.update_layout(height=800)
  return fig


def serve_plot():
  """Serve dash app plot."""
  fig = create_fig()
  fig.layout.title = 'Data from last 24 hours'
  fig.layout.xaxis.rangeslider.visible = True

  return html.Div(children=[
      html.H1(children='bairy'),
      html.Div(children='Display sensor data from Raspberry Pi.'),
      dcc.Graph(id='graph_day', figure=fig)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
dash_plot.layout = serve_plot
