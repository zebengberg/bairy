"""Launch uvicorn server and process requests with FastAPI."""


import os
import socket
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from airview.device.configs import DATE_FORMAT, CONFIGS, LOG_PATH, DATA_PATH


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
  print('Local IP address:', ip)


print_local_ip_address()
SENSOR_NAMES: list[str] = [s['name'] for s in CONFIGS['sensors']]
configure_logging(LOG_PATH)
app = FastAPI()


@app.get('/')
async def root():
  """Get most recent row in data as dictionary."""

  # fast approach to get final line of a file
  # see https://stackoverflow.com/questions/46258499/
  with open(DATA_PATH, 'rb') as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
      f.seek(-2, os.SEEK_CUR)
    last_line = f.readline().decode()
    values = last_line.split(',')
    time = values.pop(0)
    values = [int(v) for v in values]
    return {'time': time} | dict(zip(SENSOR_NAMES, values))


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
  uvicorn.run(app, host='0.0.0.0', port=8000)
