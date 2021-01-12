"""Create dash plot and dash table as endpoints."""

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from dash import Dash
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from bairy.device.configs import DATA_PATH


def preprocess_df(time_as_str: bool = False, only_last_day: bool = False):
  """Preprocess pandas DataFrame."""
  df = pd.read_csv(DATA_PATH)
  df = df.set_index('time')

  cols_to_keep = ['random', 'ir_state', 'pm_2.5', 'pm_10']
  cols_to_keep = [col for col in cols_to_keep if col in df.columns]
  df = df[cols_to_keep]
  # thresholds: 150 for pm10, 35 for pm2.5

  df.index = pd.to_datetime(df.index)
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
    if len(df) < 1000:
      return df
    df = df.resample(r).mean()
  return df


def create_fig(only_last_day: bool = False):
  """Create plotly figure using one or two y-axes."""
  df = preprocess_df(only_last_day=only_last_day)

  if 'pm_2.5' in df.columns and 'ir_state' in df.columns:
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig1 = px.line(df, x='time', y=['pm_2.5', 'pm_10'])
    fig2 = px.line(df, x='time', y=['ir_state'])
    fig2.update_traces(yaxis='y2')
    fig.add_traces(fig1.data + fig2.data)

    # ensuring no duplicate colors
    fig.for_each_trace(lambda t: t.update(line={'color': t.marker.color}))
    fig.layout.xaxis.title = 'time'
    fig.layout.yaxis.title = 'microgram / m^3'
    fig.layout.yaxis2.title = 'ir state'

    return fig

  return px.line(df, x='time', y=df.columns)


def serve_plot():
  """Dynamically serve dash_plot.layout."""
  fig_all = create_fig(False)
  fig_all.layout.height = 600
  fig_all.layout.title = 'All data'
  fig_all.layout.xaxis.rangeslider.visible = True

  fig_day = create_fig(True)
  fig_day.layout.height = 600
  fig_all.layout.title = 'Last 24 hours'
  fig_day.layout.xaxis.rangeslider.visible = True

  return html.Div(children=[
      html.H1(children='bairy'),
      html.Div(children='Display sensor data from Raspberry Pi.'),
      dcc.Graph(id='graph_all', figure=fig_all),
      dcc.Graph(id='graph_day', figure=fig_day)])


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_plot.layout = serve_plot


def serve_table():
  """Dynamically serve updated dash_table.layout."""
  df = preprocess_df(True, True)
  columns = [{'name': i, 'id': i} for i in df.columns]
  data = df.to_dict('records')
  return html.Div(children=[
      html.H1(children='bairy'),
      html.Div(children='Display data from Raspberry Pi.'),
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
