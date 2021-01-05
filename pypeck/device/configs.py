"""Read and define configurations for device."""

import os
import shutil
import json
import sys
from typing import Any

# creating ~/pypeck_data/device
DATA_DIR = os.path.expanduser('~')
for d in ['pypeck_data', 'device']:
  DATA_DIR = os.path.join(DATA_DIR, d)  # type: ignore
  if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

CONFIGS_PATH = os.path.join(DATA_DIR, 'configs.json')
TEST_CONFIGS_PATH = os.path.join(
    os.path.dirname(__file__), 'test_configs.json')


if not os.path.exists(CONFIGS_PATH):
  print('No configs.json found. Running device in test mode.')
  CONFIGS_PATH = TEST_CONFIGS_PATH  # type: ignore


with open(CONFIGS_PATH) as configs_file:
  CONFIGS: dict[str, Any] = json.load(configs_file)


LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def verify_configs(path: str):
  """Verify that the keys and types of passed configs agree with test configs."""
  with open(TEST_CONFIGS_PATH) as f:
    test_configs = json.load(f)
  with open(path) as f:
    configs = json.load(f)
  for k in test_configs:
    if k not in configs:
      raise KeyError(f'Excepted key {k} in configs.')
    if not isinstance(configs[k], type(test_configs[k])):
      raise TypeError(f'Wrong type encountered with key {k}.')


def copy_configs(path: str):
  """Copy passed configs file to pypeck_data directory."""
  target = os.path.join(DATA_DIR, 'configs.json')
  if os.path.exists(target):
    raise FileExistsError(f'Found an existing configs file at {target}.')
  shutil.copyfile(path, target)


if __name__ == '__main__':
  try:
    configs_path = sys.argv[1]
  except IndexError as e:
    raise IndexError('Expected one command line argument.') from e

  verify_configs(configs_path)
  copy_configs(configs_path)
