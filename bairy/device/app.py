"""Process device requests with FastAPI."""


from __future__ import annotations
import os
import json
import subprocess
import sys
import logging
from fastapi import FastAPI
from fastapi import responses
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
from bairy import log_configs
from bairy.device import utils, configs, dash_app, device


app = FastAPI()
app.mount('/plot', WSGIMiddleware(dash_app.dash_plot.server))
app.mount('/table', WSGIMiddleware(dash_app.dash_table.server))


@app.get('/')
def root():
  """Redirect to plot."""
  return responses.RedirectResponse(url='/plot')


@app.get('/data')
def data():
  """Return streaming response of CSV containing all data."""
  # cannot use with ... here
  f = open(configs.DATA_PATH, 'rb')
  return responses.StreamingResponse(f, media_type='text/csv')


@app.get('/logs', response_class=responses.PlainTextResponse)
def logs():
  """Return app log as plain text."""
  with open(configs.LOG_PATH) as f:
    lines = f.readlines()
  # return as reverse chronological
  lines.reverse()
  return ''.join(lines)


@app.get('/status', response_class=responses.PlainTextResponse)
def status():
  """Return device status as plaintext json."""
  device_configs = configs.load_device().dict()
  size = utils.get_data_size()
  n_rows = utils.count_rows(configs.DATA_PATH)
  latest = utils.latest_data()
  ip_address = utils.get_local_ip_address()
  disk_space = utils.get_disk_space()
  bairy_version = utils.get_bairy_version()

  device_status = {'device_configs': device_configs,
                   'data_details': {'file_size': size, 'n_rows': n_rows},
                   'available_disk_space': disk_space,
                   'bairy_version': bairy_version,
                   'ip_address': ip_address,
                   'latest_reading': latest}
  return json.dumps(device_status, indent=4)


@app.get('/remote/{command}', response_class=responses.PlainTextResponse)
def remote(command: str):
  """Run remote command on device."""
  if command == 'reboot':
    logging.info('Reboot requested')
    try:
      subprocess.check_call(['sudo', 'reboot'])
    except subprocess.CalledProcessError as e:
      pass
    return 'rebooting'

  if command == 'update':
    logging.info('Update requested')
    call = [sys.executable, '-m', 'pip', 'install', '-U', 'bairy']
    try:
      subprocess.check_call(call)
      logging.info('Update success')
      return 'success'
    except subprocess.CalledProcessError as e:
      logging.error('Update failure')
      logging.error(e)
      return 'fail'

  elif command == 'remove-data':
    logging.info('Remove data requested')
    os.remove(configs.DATA_PATH)
    device.initialize_device()  # create new data.csv with headers
    return 'success'

  elif command == 'remove-logs':
    logging.info('Remove logs requested')
    with open(configs.LOG_PATH, 'w') as f:
      f.close()
    logging.info('Logs cleared')
    return 'success'

  return 'unknown command'


@app.post('/set-configs')
def set_configs(d: device.DeviceConfigs):
  """Set device config file remotely."""
  logging.info('setting new configs')
  logging.info(d)
  assert d == device.DeviceConfigs(**d.dict())
  with open(configs.CONFIGS_PATH, 'w') as f:
    json.dump(d.dict(), f, indent=4)
  return 'new configs will be active after reboot'


def run_app():
  """Run app with uvicorn."""
  uvicorn.run(
      app,
      host='0.0.0.0',
      port=8000,
      log_config=log_configs.get_uvicorn_logger(configs.LOG_PATH)
  )
