"""A module holding utility functions for device."""

from __future__ import annotations
import logging
import os
import socket
from bairy.device.configs import DATA_PATH, LOG_FORMAT, DATE_FORMAT


def configure_logging(log_path: str):
  """Set up root logger to send logs to file and console."""
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
  file_handler = logging.FileHandler(log_path)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)


def read_headers():
  """Read first line of data."""
  with open(DATA_PATH) as f:
    headers = f.readline()
    return headers.rstrip()


def read_last_line():
  """Read last line of data."""
  # fast approach to get final line of a file
  # see https://stackoverflow.com/questions/46258499/
  with open(DATA_PATH, 'rb') as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
      f.seek(-2, os.SEEK_CUR)
    return f.readline().decode()


def latest_data():
  """Get last line of data as dictionary."""
  last_line = read_last_line()
  values = last_line.split(',')
  time = values.pop(0)
  values = [int(v) for v in values]

  d: dict[str, str | int] = {'time': time}
  headers = read_headers().split(',')[1:]
  d.update(dict(zip(headers, values)))
  return d


def get_data_size():
  """Return the size of the data file as a string."""
  n = os.path.getsize(DATA_PATH)
  for unit in ['', 'Ki', 'Mi', 'Gi']:
    if n < 1024.0:
      return f'{n:.2f} {unit}B'
    n /= 1024.0
  raise OverflowError


def count_rows(path: str):
  """Count number of rows in CSV at path."""
  assert path[-4:] == '.csv'
  with open(path) as f:
    return sum(1 for _ in f)


def print_local_ip_address():
  """See https://stackoverflow.com/questions/166506/"""

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 80))
  ip = s.getsockname()[0]
  s.close()
  print('#' * 65)
  print('LOCAL IP ADDRESS:', ip)
  print('#' * 65)
