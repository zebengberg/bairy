"""Read and define configurations and paths for device."""

from __future__ import annotations
import os
import json
from typing import Any
from bairy.device.validate import random_configs, DeviceConfigs


# creating data directory
MODULE_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.dirname(MODULE_DIR)
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')
DEVICE_DATA_DIR = os.path.join(DATA_DIR, 'device')
CONFIGS_PATH = os.path.join(DEVICE_DATA_DIR, 'configs.json')
LOG_PATH = os.path.join(DEVICE_DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DEVICE_DATA_DIR, 'data.csv')
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
  print('Successfully validated and set configs.')


def set_random_configs():
  """Save random configs as json file within data directory."""
  d = random_configs()
  assert d == DeviceConfigs(**d.dict())
  with open(CONFIGS_PATH, 'w') as f:
    json.dump(d.dict(), f, indent=4)


def load_device():
  """Look for stored configs.json file."""
  if os.path.exists(CONFIGS_PATH):
    with open(CONFIGS_PATH) as f:
      configs: dict[str, Any] = json.load(f)
    d = DeviceConfigs(**configs)
    assert d == DeviceConfigs(**configs)
    return d
  raise FileNotFoundError('No configurations found! Run bairy --help')
