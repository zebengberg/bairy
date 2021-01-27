"""Dash app to plot device data."""

import os
import glob
import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from bairy.hub.configs import BACKUP_DIR, HUB_DATA_DIR, load_ips, IP_PATH
from bairy.device import configs as device_configs
from bairy.device.dash_app import resample_df


def load_data(only_last_day: bool):
  """Load cached data."""

  ip_addresses = load_ips()
  dfs = glob.glob(HUB_DATA_DIR + '/*.csv')
  names = [f.split('/')[-1].split('.')[0] for f in dfs]

  # looking for copy in hub/backup to use instead
  for i, name in enumerate(names):
    backup_csv = os.path.join(BACKUP_DIR, name + '.csv')
    if os.path.exists(backup_csv):
      dfs[i] = backup_csv

  if 'self' in ip_addresses and os.path.exists(device_configs.DATA_PATH):
    dfs.append(device_configs.DATA_PATH)
    names.append(device_configs.load_device().name)

  dfs = [pd.read_csv(f) for f in dfs]

  # must include time
  cols_to_keep = ['time', 'pm_2.5', 'pm_1.0']
  dfs = [df[cols_to_keep]
         for df in dfs if set(cols_to_keep).issubset(set(df.columns))]

  dfs = [df.set_index(pd.to_datetime(df['time'])) for df in dfs]

  # dfs = [df.drop('time', axis=1) for df in dfs]
  dfs = [df.rename(columns={k: name + ' ' + k for k in df.columns})
         for df, name in zip(dfs, names)]

  df = pd.concat(dfs)
  if only_last_day:
    start = pd.Timestamp.now() - pd.Timedelta('1 day')
    df = df[df.index > start]
  df = resample_df(df)
  return df


def create_fig(only_last_day: bool):
  """Create plotly figure using one or two y-axes."""

  # avoiding errors when device not configured to run as hub
  if not os.path.exists(IP_PATH):
    return px.line()

  try:
    df = load_data(only_last_day)
    fig = px.line(df, x=df.index, y=df.columns)

    # showing pm2.5 safe threshold in any column exceeds
    for k in df.columns:
      if 'pm_2.5' in k:
        if df[k].max() > 40:
          fig.add_trace(go.Scatter(
              x=df.index,
              y=[35] * len(df),
              name='pm_2.5 safe threshold',
              line={'dash': 'dot'}))
          break

    if only_last_day:
      title = 'Data over last 24 hours'
    else:
      title = 'Data over entire runtime'
    fig.update_layout(height=800, title=title)
    fig.layout.xaxis.rangeslider.visible = True
    fig.layout.yaxis.title = 'micrograms / cubic meter'
    return fig

  except (KeyError, FileNotFoundError, ValueError) as e:
    logging.info(e)
    return px.line()


def serve_plot():
  """Serve dash app plot."""
  fig_day = create_fig(True)
  fig_all = create_fig(False)

  return html.Div(children=[
      html.Div(children=[
          html.H1(children='bairy', style={'fontWeight': 'bold'}),
          html.H3(children='Display sensor data from Raspberry Pi.'),
          html.A(
              'about bairy',
              href='https://github.com/zebengberg/bairy',
              style={'margin': '20px'})]),
      dcc.Graph(id='graph_day', figure=fig_day),
      dcc.Graph(id='graph_all', figure=fig_all)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
dash_plot.layout = serve_plot
