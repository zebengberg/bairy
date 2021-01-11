"""Launch uvicorn server and process requests with FastAPI."""


from __future__ import annotations
import os
from multiprocessing import Process
import socket
import pandas as pd
import plotly.express as px
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from starlette.middleware.wsgi import WSGIMiddleware
from dash import Dash
from dash.dependencies import Input, Output
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
from pypeck.device.configs import DATE_FORMAT, LOG_FORMAT, LOG_PATH, DATA_PATH
from pypeck.device.configs import load_configs, read_last_line, read_headers
from pypeck.device.device import run_device

DEVICES = load_configs()


def print_local_ip_address():
  """See https://stackoverflow.com/questions/166506/"""

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 80))
  ip = s.getsockname()[0]
  s.close()
  print('#' * 65)
  print('LOCAL IP ADDRESS:', ip)
  print('#' * 65)


def configure_app_logging(log_path: str):
  """Configure uvicorn default logging to save to file."""

  # changing default formatting
  LOGGING_CONFIG['formatters']['access']['fmt'] = LOG_FORMAT
  LOGGING_CONFIG['formatters']['access']['datefmt'] = DATE_FORMAT
  LOGGING_CONFIG['formatters']['default']['fmt'] = LOG_FORMAT
  LOGGING_CONFIG['formatters']['default']['datefmt'] = DATE_FORMAT

  # adding FileHandler to LOGGING_CONFIG
  LOGGING_CONFIG['handlers']['default_file'] = {
      'formatter': 'default',
      'class': 'logging.FileHandler',
      'filename': log_path}
  LOGGING_CONFIG['handlers']['access_file'] = {
      'formatter': 'access',
      'class': 'logging.FileHandler',
      'filename': log_path}

  # telling loggers to use the additional handler
  LOGGING_CONFIG['loggers']['uvicorn']['handlers'].append('default_file')
  LOGGING_CONFIG['loggers']['uvicorn.access']['handlers'].append('access_file')


print_local_ip_address()
configure_app_logging(LOG_PATH)
app = FastAPI()


def preprocess_df(resample_rule: str = '1T'):
  """Preprocess pandas DataFrame keeping n_rows rows."""
  df = pd.read_csv(DATA_PATH)
  df = df.set_index('time')
  cols_to_keep = []
  sensor_types = [s.sensor_type for s in DEVICES.sensors]
  if 'random' in sensor_types:
    cols_to_keep.append('random')
  if 'ir' in sensor_types:
    cols_to_keep.append('ir_value')
  if 'air' in sensor_types:
    cols_to_keep += ['pm_2.5', 'pm_10']
    # https://www.epa.gov/pm-pollution/final-decision-retain-national-ambient-air-quality-standards-particulate-matter-pm
    if df['pm_10'].max() > 150:
      df['pm_10_threshold'] = 150
      cols_to_keep.append('pm_10_threshold')
    if df['pm_2.5'].max() > 35:
      df['pm_2.5_threshold'] = 150
      cols_to_keep.append('pm_2.5_threshold')
  df = df[cols_to_keep]

  df.index = pd.to_datetime(df.index)
  df = df.resample(resample_rule).mean()  # rolling average every minute

  # keeping only last 24 hours
  start = pd.Timestamp.now() - pd.Timedelta('1 day')
  df = df[df.index > start]

  df = df.iloc[::-1]  # reversing
  df = df.reset_index()  # move time back as a column
  df['time'] = df['time'].astype(str)
  return df


css = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/united/bootstrap.min.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
app.mount('/plot', WSGIMiddleware(dash_plot.server))
dash_plot.layout = html.Div(children=[
    html.H1(children='pypeck'),
    html.Div(children='Display data from Raspberry Pi.'),
    html.Div(children=[
        html.Button(id='reload', children='reload data'),
        html.Button(id='smooth', children='smooth data'),
    ]),
    dcc.Graph(id='graph')])


@dash_plot.callback([Output('graph', 'figure'), Output('smooth', 'children')],
                    [Input('reload', 'n_clicks'), Input('smooth', 'n_clicks')])
def update_plot(n_reloads: int | None, n_smooths: int | None):
  """Update data on dash_plot when button is clicked."""
  # hacky way to get toggle state of button -- check parity of n_clicks
  print(n_reloads, n_smooths)
  if n_smooths is not None and n_smooths % 2:
    df = preprocess_df('10T')
    text = 'unsmooth data'
  else:
    df = preprocess_df()
    text = 'smooth data'
  return px.line(df, x='time', y=df.columns, title='Sensor Readings'), text


dash_table = Dash(requests_pathname_prefix='/table/',
                  external_stylesheets=[css])
app.mount('/table', WSGIMiddleware(dash_table.server))

dash_table.layout = html.Div(children=[
    html.H1(children='pypeck'),
    html.Div(children='Display data from Raspberry Pi.'),
    html.Button(id='button', children='reload data'),
    DataTable(
        id='table',
        style_cell=dict(textAlign='left'),
        style_header=dict(backgroundColor="paleturquoise"),
        style_data=dict(backgroundColor="lavender"))])


@dash_table.callback([Output('table', 'columns'), Output('table', 'data')],
                     Input('button', 'n_clicks'))
def update_table(n_clicks: int):
  """Generate a DashTable for the /table endpoint."""
  df = preprocess_df()
  columns = [{'name': i, 'id': i} for i in df.columns]
  data = df.to_dict('records')
  return columns, data


@app.get('/')
async def root():
  """Get most recent row in data as dictionary."""

  last_line = read_last_line()
  values = last_line.split(',')
  time = values.pop(0)
  values = [int(v) for v in values]

  d: dict[str, str | int] = {'time': time}
  headers = read_headers().split(',')[1:]
  d.update(dict(zip(headers, values)))
  return d


@app.get('/data')
def data():
  """Return CSV containing all data."""
  # cannot use with ... here
  f = open(DATA_PATH, 'rb')
  return StreamingResponse(f, media_type='text/csv')


@app.get('/logs', response_class=PlainTextResponse)
async def logs():
  """Return the log data."""
  with open(LOG_PATH) as f:
    return f.read()


@app.get('/configs')
async def configs():
  """Return the device config."""
  return DEVICES.dict()


@app.get('/size')
async def size():
  """Return the size in bytes of the data file."""
  return os.path.getsize(DATA_PATH)


def run_app():
  """Run app as separate process."""
  uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
  p = Process(target=run_app)
  p.start()
  run_device()
