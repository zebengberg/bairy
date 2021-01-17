"""Read and define addresses and paths for the hub."""

from __future__ import annotations
import os
import sys
import glob
import ipaddress
import json


# creating data directory within module
MODULE_DIR = os.path.dirname(__file__)
PACKAGE_DIR = os.path.dirname(MODULE_DIR)
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')
HUB_DATA_DIR = os.path.join(DATA_DIR, 'hub')
BACKUP_DIR = os.path.join(HUB_DATA_DIR, 'backup')
IP_PATH = os.path.join(HUB_DATA_DIR, 'ip_addresses.json')
LOG_PATH = os.path.join(HUB_DATA_DIR, 'app.logs')
RECACHE_INTERVAL = 60 * 60  # update every hour
if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)
if not os.path.exists(HUB_DATA_DIR):
  os.mkdir(HUB_DATA_DIR)
if not os.path.exists(BACKUP_DIR):
  os.mkdir(BACKUP_DIR)


def set_ips(path: str):
  """Verify and save device IP addresses in data directory."""
  with open(path) as f:
    addresses = f.read().splitlines()
  for a in addresses:
    try:
      ipaddress.ip_address(a)
    except ValueError as e:
      if a != 'self':
        raise e
  with open(IP_PATH, 'w') as f:
    json.dump(addresses, f)


def load_ips() -> list[str]:
  """Read IP addresses saved in data directory."""
  with open(IP_PATH) as f:
    return json.load(f)


if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise ValueError('Expected path/to/ip_addresses.txt as additional arg!')
  arg = sys.argv[1]
  if arg == '--remove-addresses':
    os.remove(IP_PATH)
    print(f'Removed stored file at {IP_PATH}')
  elif arg == '--remove-data':
    for data_file in glob.glob(DATA_DIR + '*.csv'):
      os.remove(data_file)
    print('Removed all stored data.')
  elif arg == '--remove-logs':
    os.remove(LOG_PATH)
    print(f'Removed stored file at {LOG_PATH}')

  else:
    set_ips(arg)
    print('Successfully set IP addresses')
