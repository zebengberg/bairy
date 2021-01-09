"""Read and define configurations for device."""

from __future__ import annotations
import os
import json


# creating ~/pypeck_data/device/data
MODULE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(MODULE_DIR, 'data')
PACKAGE_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))

if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)


def load_test_configs():
  """Load test configs shipped with module."""
  with open(os.path.join(MODULE_DIR, 'test_configs.json')) as f:
    configs: dict[str, str | int | list[str]] = json.load(f)
  return configs


TEST_CONFIGS = load_test_configs()


def load_configs():
  """Look for configs.json in several places with project."""
  path = os.path.join(PACKAGE_DIR, 'configs.json')

  if not os.path.exists(path):
    path = os.path.join(PACKAGE_DIR, 'pypeck', 'configs.json')
    if not os.path.exists(path):
      path = os.path.join(MODULE_DIR, 'configs.json')
      print('No configs.json found. Running device in test mode.')
      return TEST_CONFIGS

  with open(path) as configs_file:
    configs: dict[str, str | int | list[str]] = json.load(configs_file)
  return configs


CONFIGS = load_configs()


def verify_configs():
  """Verify that the keys and types of passed configs agree with test configs."""
  for k in TEST_CONFIGS:
    if k not in CONFIGS:
      raise KeyError(f'Excepted key {k} in configs.json.')
    if not isinstance(CONFIGS[k], type(TEST_CONFIGS[k])):
      raise TypeError(f'Wrong type encountered with key {k} in configsjson.')


verify_configs()


LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def read_last_line():
  """Read last line of data."""
  # fast approach to get final line of a file
  # see https://stackoverflow.com/questions/46258499/
  with open(DATA_PATH, 'rb') as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
      f.seek(-2, os.SEEK_CUR)
    return f.readline().decode()


def read_headers():
  """Read first line of data."""
  with open(DATA_PATH) as f:
    headers = f.readline()
    return headers.rstrip()
