"""Read and define configurations and paths for device."""

from __future__ import annotations
import os
import sys
import json
from typing import Any
from bairy.device.validate import example_configs, random_configs, DeviceConfigs


# creating data directory
MODULE_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.dirname(MODULE_DIR)
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')
DEVICE_DATA_DIR = os.path.join(DATA_DIR, 'device')
CONFIGS_PATH = os.path.join(DEVICE_DATA_DIR, 'configs.json')
LOG_PATH = os.path.join(DEVICE_DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DEVICE_DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)
if not os.path.exists(DEVICE_DATA_DIR):
  os.mkdir(DEVICE_DATA_DIR)


def set_configs(path: str):
  """Verify and save device configs as json file within data directory."""
  with open(path) as f:
    configs: dict[str, Any] = json.load(f)
  d = DeviceConfigs(**configs)
  assert d == DeviceConfigs(**d.dict())
  with open(CONFIGS_PATH, 'w') as f:
    json.dump(configs, f, indent=4)


def set_random_configs():
  """Save random configs as json file within data directory."""
  d = random_configs()
  assert d == DeviceConfigs(**d.dict())
  with open(CONFIGS_PATH, 'w') as f:
    json.dump(d.dict(), f, indent=4)


def load_configs():
  """Look for stored configs.json file."""
  if os.path.exists(CONFIGS_PATH):
    with open(CONFIGS_PATH) as f:
      configs: dict[str, Any] = json.load(f)
    d = DeviceConfigs(**configs)
    assert d == DeviceConfigs(**configs)
    return d
  else:
    raise FileNotFoundError('No configurations found! Run bairy --help')


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('Expected path/to/configs.json as additional argument!')
    print('Create a configs.json, and run with:')
    print(' $ python3 -m bairy.device.configs configs.json')
    print('Below is an example of a valid configs.json schema.')
    print(example_configs().json(indent=4))

  else:
    arg = sys.argv[1]
    if arg == '--remove-configs':
      os.remove(CONFIGS_PATH)
      print(f'Removed stored file at {CONFIGS_PATH}')
    elif arg == '--remove-data':
      os.remove(DATA_PATH)
      print(f'Removed stored file at {DATA_PATH}')
    elif arg == '--remove-logs':
      os.remove(LOG_PATH)
      print(f'Removed stored file at {LOG_PATH}')
    else:
      set_configs(arg)
      print('Successfully validated and set configs.')
