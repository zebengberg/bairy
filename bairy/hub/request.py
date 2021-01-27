"""Gather configuration and data from devices."""

from __future__ import annotations
from typing import Any
import logging
import os
import json
import asyncio
import nest_asyncio
import aiohttp
from bairy.hub import configs
from bairy.device import utils, configs as device_configs, app as device_app


nest_asyncio.apply()


async def get_status(ip_address: str):
  """Get status of device associated to ip_address."""
  if ip_address == 'self':
    status_as_str = device_app.status()
    d: dict[str, Any] = json.loads(status_as_str)
    return d

  async with aiohttp.ClientSession() as session:
    url = 'http://' + ip_address + ':8000/' + 'status'
    async with session.get(url) as r:
      d: dict[str, Any] = await r.json()
      return d


def get_all_statuses():
  """Get status of every device known to hub."""
  ip_addresses = configs.load_ips()
  tasks = [get_status(ip_address) for ip_address in ip_addresses]
  gathered = asyncio.gather(*tasks)

  loop = asyncio.get_event_loop()
  statuses = loop.run_until_complete(gathered)
  return statuses


def validate_names():
  """Check device names to guarantee no duplicates."""
  statuses = get_all_statuses()
  names = [s['device_configs']['name'] for s in statuses]
  if len(set(names)) < len(list(names)):
    raise ValueError('Discovered repeated name within devices!')
  logging.info('Validated device names %s', names)


async def get_data(ip_address: str):
  """Request /data endpoint from device and save response to file."""
  try:
    status = await get_status(ip_address)
    name: str = status['device_configs']['name']
    data_path = os.path.join(configs.HUB_DATA_DIR, name + '.csv')

    if ip_address == 'self':  # making a symlink to data
      os.symlink(device_configs.DATA_PATH, data_path)

    url = 'http://' + ip_address + ':8000/data'

    # make a backup copy of existing data
    backup_path = os.path.join(configs.BACKUP_DIR, name + '.csv')
    if os.path.exists(data_path):
      os.rename(data_path, backup_path)

    logging.info('Requesting data from %s', ip_address)
    await stream_request(url, data_path)

    # comparing the number of rows of the new data with the old data
    size = utils.count_rows(data_path)
    if os.path.exists(backup_path):
      if size < utils.count_rows(backup_path):
        raise ValueError('New data is missing some of previous data.')
      os.remove(backup_path)
    logging.info('Successfully saved data from %s', ip_address)

  except aiohttp.ClientConnectionError as e:
    logging.error('Failed to connect to %s', ip_address)
    logging.error(e)


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


async def request_data_indefinitely(ip_address: str):
  """Request data from each device indefinitely."""
  assert ip_address != 'self'
  while True:
    await get_data(ip_address)
    await asyncio.sleep(configs.RECACHE_INTERVAL)


async def run_requests():
  """Run requests indefinitely."""
  ip_addresses = configs.load_ips()
  tasks = [request_data_indefinitely(
      ip_address) for ip_address in ip_addresses if ip_address != 'self']
  return await asyncio.gather(*tasks)
