"""Create dash plot and dash table as endpoints."""

import pandas as pd
import plotly.express as px
from dash import Dash
from dash.dependencies import Input, Output
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from pypeck.device.configs import DATA_PATH


def preprocess_df():
  """Preprocess pandas DataFrame."""
  df = pd.read_csv(DATA_PATH)
  df = df.set_index('time')

  cols_to_keep = ['random', 'ir_state', 'pm_2.5', 'pm_10']
  cols_to_keep = [col for col in cols_to_keep if col in df.columns]
  df = df[cols_to_keep]
  # thresholds: 150 for pm10, 35 for pm2.5

  df.index = pd.to_datetime(df.index)
  # df = df.resample(resample_rule).mean()  # rolling average every minute

  # keeping only last 12 hours
  start = pd.Timestamp.now() - pd.Timedelta('12 hours')
  df = df[df.index > start]

  df = df.iloc[::-1]  # reversing
  df = df.reset_index()  # move time back as a column
  df['time'] = df['time'].astype(str)
  return df


def serve_plot():
  """Dynamically serve dash_plot.layout."""
  df = preprocess_df()
  fig = px.line(df, x='time', y=df.columns, title='Sensor Readings')
  return html.Div(children=[
      html.H1(children='pypeck'),
      html.Div(children='Display data from Raspberry Pi.'),
      dcc.Graph(id='graph', figure=fig)])


css = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/united/bootstrap.min.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
# See https://dash.plotly.com/live-updates
dash_plot.layout = serve_plot


def serve_table():
  """Dynamically serve updated dash_table.layout."""
  df = preprocess_df()
  columns = [{'name': i, 'id': i} for i in df.columns]
  data = df.to_dict('records')
  return html.Div(children=[
      html.H1(children='pypeck'),
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
