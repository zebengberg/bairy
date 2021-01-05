"""Gather configuration and data from devices."""

import os
import asyncio
import json
import requests


with open(os.path.join(os.path.dirname(__file__), 'addresses.json')) as f:
  IP_ADDRESSES: list[str] = json.load(f)

# creating ~/airview_data/hub
DATA_DIR = os.path.expanduser('~')
for d in ['airview_data', 'hub']:
  DATA_DIR = os.path.join(DATA_DIR, d)
  if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

UPDATE_INTERVAL = 10


def get_configs():
  pass


async def get_data():
  while True:
    await asyncio.sleep(UPDATE_INTERVAL)
    r = requests.get(IP_ADDRESSES[0])
    print(r.json())


if __name__ == '__main__':
  get_configs()
  loop = asyncio.get_event_loop()
  loop.create_task(get_data())
  loop.run_forever()
