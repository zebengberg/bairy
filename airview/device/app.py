"""Launch uvicorn server and process requests with FastAPI."""


import os
import time
import csv
from datetime import datetime
from dateutil import parser
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from airview.device.sensor import DIR_NAME, DATE_FORMAT, read_configs


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


configs = read_configs()
LOG_PATH = os.path.join(DIR_NAME, configs['log_file'])
configure_logging(LOG_PATH)
DATA_PATH = os.path.join(DIR_NAME, configs['data_file'])
app = FastAPI()


@app.get('/')
async def root():
  """Get most recent data point."""

  # fast approach to get final line of a file
  # see https://stackoverflow.com/questions/46258499/
  with open(DATA_PATH, 'rb') as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
      f.seek(-2, os.SEEK_CUR)
    last_line = f.readline().decode()
    t, v = last_line.split(',')
    return {'time': t, 'value': int(v)}


@app.get('/data/')
async def data(date: str):
  """Get all data not previously checked in."""
  try:
    dt = parser.parse(date)
  except parser.ParserError as e:
    raise HTTPException(status_code=400, detail=str(e)) from e
  with open(DATA_PATH) as f:
    pass


@app.get('/logs/', response_class=PlainTextResponse)
async def logs():
  """Return the log data."""
  with open(LOG_PATH) as f:
    return f.read()


if __name__ == '__main__':
  uvicorn.run(app, host='0.0.0.0', port=8000)
