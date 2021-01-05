"""Gather configuration and data from devices."""

import os
import asyncio
import json
from typing import Any
from datetime import datetime
import requests
from pypeck.device.configs import DATE_FORMAT


with open(os.path.join(os.path.dirname(__file__), 'addresses.json')) as addr:
  IP_ADDRESSES: list[str] = json.load(addr)

# creating ~/pypeck_/hub
DATA_DIR = os.path.expanduser('~')
for dir_name in ['pypeck_data', 'hub']:
  DATA_DIR = os.path.join(DATA_DIR, dir_name)
  if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

UPDATE_INTERVAL = 60 * 60  # update every hour


def get_devices():
  """Get, check, and save meta-data for devices."""
  devices: list[dict[str, Any]] = []
  for i in IP_ADDRESSES:
    url = 'http://' + i + ':8000/configs'
    r = requests.get(url)
    configs: dict[str, Any] = r.json()
    configs.update({'ip_address': i})
    devices.append(configs)
  check_devices(devices)
  save_devices(devices)
  return devices


def check_devices(devices: list[dict[str, Any]]):
  """Check devices dictionary for repeated names."""
  names = [d['name'] for d in devices]
  if len(names) != len(set(names)):
    raise ValueError(f'Repeated names found in devices:\n{names}')


def save_devices(devices: list[dict[str, Any]]):
  """Write device meta-data to file."""
  path = os.path.join(DATA_DIR, 'devices.json')
  if not os.path.exists(path):
    with open(path, 'w') as f:
      json.dump(devices, f)


def get_data(device: dict[str, Any]):
  """Request /data endpoint from device and save response to file."""
  url = 'http://' + device['ip_address'] + ':8000/data'
  r = requests.get(url)
  path = os.path.join(DATA_DIR, (name := device['name']) + '.csv')

  # make a backup copy of existing data
  backup_path = os.path.join(DATA_DIR, name + '_backup.csv')
  if os.path.exists(path):
    os.rename(path, backup_path)

  # write response
  with open(path, 'wb') as f:
    f.write(r.content)

  # remove backup copy and print message
  size = count_rows(path)
  if os.path.exists(backup_path):
    if size < count_rows(backup_path):
      raise ValueError('New data is missing some of previous data.')
    os.remove(backup_path)
  now = datetime.now().strftime(DATE_FORMAT)
  print(f'Successfully saved data from {name} at {now}.')
  print(f'The data file {name}.csv now has {size} rows.')


def count_rows(path: str):
  """Count number of rows in CSV at path."""
  with open(path) as f:
    return sum(1 for _ in f)


async def get_data_indefinitely():
  """Get data from devices every UPDATE_INTERVAL seconds."""
  devices = get_devices()
  while True:
    for d in devices:
      get_data(d)
    await asyncio.sleep(UPDATE_INTERVAL)


def get_data_once():
  """Get data from devices once and return device dictionary."""
  devices = get_devices()
  for d in devices:
    get_data(d)
  return devices


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.create_task(get_data_indefinitely())
  loop.run_forever()
