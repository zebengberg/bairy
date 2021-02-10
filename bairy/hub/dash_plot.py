"""Dash app to plot device data."""

import os
import glob
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from bairy.hub import configs


def load_data(time_period: str = 'all'):
  """Load cached data."""

  dfs = glob.glob(configs.HUB_DATA_DIR + '/*' + time_period + '.csv')
  names = [f.split('/')[-1].split('_')[0] for f in dfs]

  dfs = [pd.read_csv(f) for f in dfs]

  # must include time
  cols_to_keep = {'time', 'pm_10', 'pm_2.5', 'random1'}
  dfs = [df[cols_to_keep & set(df.columns)] for df in dfs]

  dfs = [df.set_index(pd.to_datetime(df['time'])) for df in dfs]
  dfs = [df.drop('time', axis=1) for df in dfs]
  dfs = [df.rename(columns={k: name + ' ' + k for k in df.columns})
         for df, name in zip(dfs, names)]
  if dfs == []:
    return pd.DataFrame([])
  return pd.concat(dfs)


def create_fig(time_period: str):
  """Create plotly figure using one or two y-axes."""

  # avoiding errors when device not configured to run as hub
  if not os.path.exists(configs.IP_PATH):
    return px.line()

  df = load_data(time_period)
  if df.empty:
    return px.line()

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

  if time_period == 'day':
    title = 'data over last 24 hours'
  elif time_period == 'week':
    title = 'data over last 7 days'
  else:
    title = 'data over entire runtime'

  fig.update_layout(height=800, title=title)
  fig.layout.xaxis.rangeslider.visible = True
  fig.layout.yaxis.title = 'micrograms / cubic meter'
  return fig


def serve_plot():
  """Serve dash app plot."""
  fig_day = create_fig('day')
  fig_week = create_fig('week')

  return html.Div(children=[
      html.Div(children=[
          html.H1(children='bairy', style={'fontWeight': 'bold'}),
          html.H3(children='Display sensor data from Raspberry Pi.'),
          html.A(
              'about bairy',
              href='https://github.com/zebengberg/bairy',
              style={'margin': '20px'})]),
      dcc.Graph(id='graph_day', figure=fig_day),
      dcc.Graph(id='graph_week', figure=fig_week)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(
    requests_pathname_prefix='/plot/',
    external_stylesheets=[css]
)
dash_plot.layout = serve_plot
