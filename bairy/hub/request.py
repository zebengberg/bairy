"""Gather configuration and data from devices."""

from __future__ import annotations

import os
from datetime import datetime
import asyncio
import aiohttp
from bairy.hub.configs import DATA_DIR, BACKUP_DIR, RECACHE_INTERVAL, load_ips
from bairy.device.configs import load_configs, DATE_FORMAT
from bairy.device.utils import get_data_size


async def get_endpoint(ip_address: str, endpoint: str):
  """Helper function to async request endpoint from ip_address."""
  assert endpoint[0] != '/'
  assert ip_address != 'self'
  async with aiohttp.ClientSession() as session:
    url = 'http://' + ip_address + ':8000/' + endpoint
    async with session.get(url) as r:
      return await r.json()


async def get_configs(ip_address: str):
  """Get configs associated to ip_address."""
  if ip_address == 'self':
    return load_configs().dict()
  return await get_endpoint(ip_address, 'configs')


async def get_name(ip_address: str) -> str:
  """Get name associated to ip_address."""
  if ip_address == 'self':
    return load_configs().name
  return await get_endpoint(ip_address, 'name')


async def get_size(ip_address: str) -> str:
  """Get size of data on device with ip_address."""
  if ip_address == 'self':
    return get_data_size()
  return await get_endpoint(ip_address, 'size')


def validate_names():
  """Check device names to guarantee no duplicates."""
  ip_addresses = load_ips()
  loop = asyncio.get_event_loop()
  tasks = [get_name(ip_address) for ip_address in ip_addresses]
  gathered = asyncio.gather(*tasks)
  names = loop.run_until_complete(gathered)
  if len(set(names)) < len(list(names)):
    raise ValueError('Discovered repeated name within devices!')
  print('Device names:', names)


async def get_data(ip_address: str):
  """Request /data endpoint from device and save response to file."""

  assert ip_address != 'self'

  try:
    name = await get_name(ip_address)
    url = 'http://' + ip_address + ':8000/data'

    # make a backup copy of existing data
    path = os.path.join(DATA_DIR, name + '.csv')
    backup_path = os.path.join(DATA_DIR, 'backups', name + '.csv')
    if os.path.exists(path):
      os.rename(path, backup_path)

    print('Requesting data from', ip_address)
    await stream_request(url, path)

    # remove backup copy and print message
    size = count_rows(path)
    if os.path.exists(backup_path):
      if size < count_rows(backup_path):
        raise ValueError('New data is missing some of previous data.')
      os.remove(backup_path)
    now = datetime.now().strftime(DATE_FORMAT)
    print(f'Successfully saved data from {url} at {now}.')
    print(f'The data file {name}.csv now has {size} rows.')

  except ConnectionError:
    print('Failed to connect to device')


async def stream_request(url: str, save_path: str):
  """Make stream request and save data with aiohttp."""
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as r:
      with open(save_path, 'wb') as f:
        while True:
          chunk = await r.content.read(1024)
          if not chunk:
            break
          f.write(chunk)


def count_rows(path: str):
  """Count number of rows in CSV at path."""
  with open(path) as f:
    return sum(1 for _ in f)


async def request_data_indefinitely(ip_address: str):
  """Request data from each device indefinitely."""
  assert ip_address != 'self'
  while True:
    await get_data(ip_address)
    await asyncio.sleep(RECACHE_INTERVAL)


def run_loop():
  loop = asyncio.get_event_loop()
  for ip_address in load_ips():
    if ip_address != 'self':
      loop.create_task(request_data_indefinitely(ip_address))
  loop.run_forever()


if __name__ == '__main__':
  validate_names()
  run_loop()
