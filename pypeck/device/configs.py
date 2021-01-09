"""Read and define configurations for device."""

from __future__ import annotations
import os
import sys
import json
from typing import Any


# creating data directory within module
MODULE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(MODULE_DIR, 'data')
PACKAGE_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))
CONFIGS_PATH = os.path.join(DATA_DIR, 'configs.json')
TEST_CONFIGS_PATH = os.path.join(MODULE_DIR, 'test_configs.json')
if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)


def verify_configs(configs: dict[str, Any]):
  """Verify that the keys and types of configs are as expected."""
  keys = ['name', 'location', 'sensors', 'update_interval']
  types = [str, str, list, int]
  for k, t in zip(keys, types):
    if k not in configs:
      raise KeyError(f'Expected key "{k}" in configs.')
    if not isinstance(configs[k], t):
      raise ValueError(f'Expected the "{k}" field to have type "{t}".')


def load_test_configs():
  """Load test configs shipped with module."""
  with open(TEST_CONFIGS_PATH) as f:
    configs: dict[str, Any] = json.load(f)
    verify_configs(configs)
  return configs


def set_configs(path: str):
  """Verify and save device configs as json file within data directory."""
  with open(path) as f:
    configs: dict[str, Any] = json.load(f)
  verify_configs(configs)
  with open(CONFIGS_PATH, 'w') as f:
    json.dump(configs, f, indent=4)


def load_configs():
  """Look for stored configs.json file."""
  if os.path.exists(CONFIGS_PATH):
    with open(CONFIGS_PATH) as f:
      configs: dict[str, Any] = json.load(f)
      verify_configs(configs)
  else:
    print('No configs.json found. See the README for instructions.')
    print('Loading app with test configs instead.')
    configs = load_test_configs()
  return configs


LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


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


if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise ValueError('Expected path/to/configs.json as additional argument!')
  arg = sys.argv[1]
  if arg == '--remove-configs':
    os.remove(CONFIGS_PATH)
    print('Removed stored configs.json')
  elif arg == '--remove-data':
    os.remove(DATA_PATH)
    print('Removed stored data.csv')
  elif arg == '--remove-log':
    os.remove(LOG_PATH)
    print('Removed stored app.logs')

  else:
    set_configs(arg)
    print('Successfully verify and set configs.')
