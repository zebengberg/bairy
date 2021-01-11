"""Launch uvicorn server and process requests with FastAPI."""


from __future__ import annotations
import os
from multiprocessing import Process
import socket
import pandas as pd

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from starlette.middleware.wsgi import WSGIMiddleware

from pypeck.device.configs import DATE_FORMAT, LOG_FORMAT, LOG_PATH, DATA_PATH
from pypeck.device.configs import load_configs, read_last_line, read_headers
from pypeck.device.device import run_device
from pypeck.device.dash_app import dash_plot, dash_table

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
app.mount('/plot', WSGIMiddleware(dash_plot.server))
app.mount('/table', WSGIMiddleware(dash_table.server))


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
