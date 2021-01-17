"""Dash app to plot device data."""

import os
import glob
import pandas as pd
import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from bairy.hub.configs import HUB_DATA_DIR, IP_PATH, load_ips
from bairy.device import configs as device_configs
from bairy.device.dash_app import resample_df


def load_data():
  """Load cached data."""
  if os.path.exists(IP_PATH):
    ip_addresses = load_ips()
  else:
    return None

  dfs = glob.glob(HUB_DATA_DIR + '/*.csv')
  names = [f.split('/')[-1].split('.')[0] for f in dfs]

  if 'self' in ip_addresses and os.path.exists(device_configs.DATA_PATH):
    dfs.append(device_configs.DATA_PATH)
    names.append(device_configs.load_device().name)
  if dfs == []:
    return None

  dfs = [pd.read_csv(f) for f in dfs]
  dfs = [df[['time', 'pm_2.5']] for df in dfs]
  dfs = [df.set_index(pd.to_datetime(df['time'])) for df in dfs]
  dfs = [df.drop('time', axis=1) for df in dfs]
  # TODO: give better name
  dfs = [df.rename(columns={'pm_2.5': name}) for df, name in zip(dfs, names)]

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
