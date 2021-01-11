"""Read and define configurations and paths for device."""

from __future__ import annotations
import os
import sys
import json
from typing import Any
from pypeck.device.validate import example_configs, random_configs, DeviceConfigs


# creating data directory within module
MODULE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(MODULE_DIR, 'data')
CONFIGS_PATH = os.path.join(DATA_DIR, 'configs.json')
LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)


def set_configs(path: str):
  """Verify and save device configs as json file within data directory."""
  with open(path) as f:
    configs: dict[str, Any] = json.load(f)
  d = DeviceConfigs(**configs)
  assert d == DeviceConfigs(**d.dict())
  with open(CONFIGS_PATH, 'w') as f:
    json.dump(configs, f, indent=4)


def load_configs():
  """Look for stored configs.json file."""
  if os.path.exists(CONFIGS_PATH):
    with open(CONFIGS_PATH) as f:
      configs: dict[str, Any] = json.load(f)
    d = DeviceConfigs(**configs)
    assert d == DeviceConfigs(**configs)

  else:
    print('No configs.json found. See the README for instructions.')
    print('Loading app with random configs instead.')
    d = random_configs()
  return d


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
    print('Expected path/to/configs.json as additional argument!')
    print('Create a configs.json, and run with:')
    print(' $ python3 -m pypeck.device.configs configs.json')
    print('Below is an example of a valid configs.json schema.')
    print(example_configs().json(indent=4))

  else:
    arg = sys.argv[1]
    if arg == '--remove-configs':
      os.remove(CONFIGS_PATH)
      print('Removed stored configs.json')
    elif arg == '--remove-data':
      os.remove(DATA_PATH)
      print('Removed stored data.csv')
    elif arg == '--remove-logs':
      os.remove(LOG_PATH)
      print('Removed stored app.logs')
    else:
      set_configs(arg)
      print('Successfully validated and set configs.')
