"""A module holding utility functions for device."""

from __future__ import annotations
import os
import socket
import shutil
import pkg_resources
from bairy.device import configs


def read_headers():
  """Read first line of data."""
  with open(configs.DATA_PATH) as f:
    headers = f.readline()
    return headers.rstrip()


def read_last_line():
  """Read last line of data."""
  # fast approach to get final line of a file
  # see https://stackoverflow.com/questions/46258499/
  with open(configs.DATA_PATH, 'rb') as f:
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
  if not os.path.exists(configs.DATA_PATH):
    return '0'
  n = os.path.getsize(configs.DATA_PATH)
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


def get_local_ip_address():
  """See https://stackoverflow.com/questions/166506/"""

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(('8.8.8.8', 80))
  ip: str = s.getsockname()[0]
  s.close()
  return ip


def get_disk_space():
  """Get available disk space."""
  gb = shutil.disk_usage('/').free / (1 << 30)
  return f'{gb:.3f} GB'


def get_bairy_version():
  """Use pkg_resources to get bairy version."""
  return pkg_resources.get_distribution('bairy').version
