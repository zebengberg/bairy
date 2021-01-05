"""Read and define configurations for device."""

import os
import json
from typing import Any

CONFIG_FILE = 'test_config.json'
CONFIG_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
with open(CONFIG_PATH) as f:
  CONFIGS: dict[str, Any] = json.load(f)

# creating ~/airview_data/device
DATA_DIR = os.path.expanduser('~')
for d in ['airview_data', 'device']:
  DATA_DIR = os.path.join(DATA_DIR, d)
  if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)


LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
DATA_PATH = os.path.join(DATA_DIR, 'data.csv')
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
