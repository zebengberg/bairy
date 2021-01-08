"""Launch uvicorn server and process requests with FastAPI."""


from __future__ import annotations
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
import dash_core_components as dcc
import dash_html_components as html
from pypeck.device.configs import DATE_FORMAT, CONFIGS, LOG_PATH, DATA_PATH, read_last_line, read_headers


def configure_logging(log_path: str):
  """Configure uvicorn default logging to save to file."""

  # changing default formatting
  LOGGING_CONFIG['formatters']['access']['fmt'] = '%(asctime)s - %(levelname)s - %(message)s'
  LOGGING_CONFIG['formatters']['access']['datefmt'] = DATE_FORMAT
  LOGGING_CONFIG['formatters']['default']['fmt'] = '%(asctime)s - %(levelname)s - %(message)s'
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


def print_local_ip_address():
  """See https://stackoverflow.com/questions/166506/"""

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 80))
  ip = s.getsockname()[0]
  s.close()
  print('#' * 65)
  print('LOCAL IP ADDRESS:', ip)
  print('#' * 65)


print_local_ip_address()
configure_logging(LOG_PATH)
app = FastAPI()


css = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/united/bootstrap.min.css'
dash_app = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
dash_app.layout = html.Div(children=[
    html.H1(children='pypeck'),
    html.Div(children='Display data from Raspberry Pi.'),
    dcc.Graph(id='graph'),
    html.Button(id='button', children='reload data')
])


@dash_app.callback(Output('graph', 'figure'), Input('button', 'n_clicks'))
def update_plot(n_clicks: int):
  """Update plotly plot when refresh button is clicked."""
  df = pd.read_csv(DATA_PATH)
  return px.line(df, x='time', y=df.columns, title='Sensor Readings')


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
  return CONFIGS


if __name__ == '__main__':
  app.mount('/plot', WSGIMiddleware(dash_app.server))
  uvicorn.run(app, host='0.0.0.0', port=8000)
