"""Gather data from servers as the logging hub."""

import random
import asyncio
import requests

local_url = 'http://127.0.0.1:8000/'


async def update(words: list[str]):
  while True:
    for w in words:
      await asyncio.sleep(2)
      r = requests.get(local_url)
      print(w)
      print(r.text)

      await asyncio.sleep(2)
      data = {'index': [random.randint(0, 10) for _ in range(10)]}
      r = requests.post(local_url + 'received/', json=data)


loop = asyncio.get_event_loop()
loop.create_task(update(['hello', 'world']))
loop.run_forever()
