"""Launch uvicorn server and process requests with FastAPI."""


from __future__ import annotations
import os
import logging
import json
from multiprocessing import Process
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse, RedirectResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from fastapi.middleware.wsgi import WSGIMiddleware
from bairy.device.device import run_device
from bairy.device.dash_app import dash_plot, dash_table
from bairy.device import utils, configs


def configure_app_logging(log_path: str):
  """Configure uvicorn default logging to save to file."""

  # changing default formatting
  LOGGING_CONFIG['formatters']['access']['fmt'] = configs.LOG_FORMAT
  LOGGING_CONFIG['formatters']['access']['datefmt'] = configs.DATE_FORMAT
  LOGGING_CONFIG['formatters']['default']['fmt'] = configs.LOG_FORMAT
  LOGGING_CONFIG['formatters']['default']['datefmt'] = configs.DATE_FORMAT

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


utils.print_local_ip_address()
configure_app_logging(configs.LOG_PATH)
app = FastAPI()
app.mount('/plot', WSGIMiddleware(dash_plot.server))
app.mount('/table', WSGIMiddleware(dash_table.server))


@app.get('/')
async def root():
  """Redirect to docs."""
  return RedirectResponse(url='/docs')


@app.get('/data')
def data():
  """Return streaming response of CSV containing all data."""
  # cannot use with ... here
  f = open(configs.DATA_PATH, 'rb')
  return StreamingResponse(f, media_type='text/csv')


@app.get('/logs', response_class=PlainTextResponse)
async def logs():
  """Return app log as plain text."""
  with open(utils.LOG_PATH) as f:
    return f.read()


@app.get('/status', response_class=PlainTextResponse)
def status():
  """Return device status as plaintext json."""
  device_status = status_json()
  return json.dumps(device_status, indent=4)


@app.get('/status.json')
def status_json():
  """Return device status as raw json."""
  device_configs = configs.load_configs().dict()
  size = utils.get_data_size()
  n_rows = utils.count_rows(utils.DATA_PATH)
  latest = utils.latest_data()
  device_status = {'device_configs': device_configs,
                   'data_details': {'file_size': size, 'n_rows': n_rows},
                   'latest_reading': latest}
  return device_status


@app.get('/experiment/{param}')
def experiment(param: str):
  """Run experimental param on device."""
  if param == 'reboot':
    os.system('sudo reboot')
  elif param == 'update':
    pass
  else:
    return 'unknown param'


def run_app():
  """Run app as separate process."""
  uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
  p = Process(target=run_app)
  p.start()
  run_device()
