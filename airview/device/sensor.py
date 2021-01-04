"""Read sensor values and write data to disk."""

import os
import asyncio
import random
import json
from datetime import datetime


class Sensor:
  def __init__(self):
    dir_name = os.path.dirname(__file__)
    config_path = os.path.join(dir_name, 'config.json')
    with open(config_path) as f:
      configs = json.load(f)

    self.name: str = configs['name']
    self.data_file: str = os.path.join(dir_name, configs['data_file'])
    self.create_data_file()
    self.pin: int = configs['pin']
    self.update_interval: int = configs['update_interval']
    self.test_mode = self.name == 'test'

  def create_data_file(self):
    """Create data file if none exists."""
    if not os.path.exists(self.data_file):
      with open(self.data_file, 'w') as f:
        f.write('time,value\n')

  def read_sensor(self):
    """Read sensor value."""
    if self.test_mode:
      return random.randint(0, 1023)
    return None  # TODO: replace with gpio reading

  def write_data(self):
    """Create a data file if none exists and append data to end."""
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    value = self.read_sensor()
    row = time + ',' + str(value) + '\n'
    with open(self.data_file, 'a') as f:
      f.write(row)

  async def run(self):
    """Call write_data indefinitely."""
    while True:
      await asyncio.sleep(self.update_interval)
      self.write_data()


if __name__ == '__main__':
  s = Sensor()
  loop = asyncio.get_event_loop()
  loop.create_task(s.run())
  loop.run_forever()
