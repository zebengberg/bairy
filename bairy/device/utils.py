"""A module holding utility functions for device."""

import os
from bairy.device.configs import DATA_PATH


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


def get_data_size():
  """Return the size of the data file as a string."""
  n = os.path.getsize(DATA_PATH)
  for unit in ['', 'Ki', 'Mi', 'Gi']:
    if n < 1024.0:
      return f'{n:.2f} {unit}B'
    n /= 1024.0
  raise OverflowError
