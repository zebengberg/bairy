"""Read sensor values and write data to disk."""

import os
import asyncio
import random
import json
from datetime import datetime


DIR_NAME = os.path.dirname(__file__)
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
CONFIG_FILE = 'test_config.json'


def read_configs():
  """Read configs.json."""
  config_path = os.path.join(DIR_NAME, CONFIG_FILE)
  with open(config_path) as f:
    return json.load(f)


class Sensor:
  def __init__(self):
    configs = read_configs()
    self.name: str = configs['name']
    self.data_file: str = os.path.join(DIR_NAME, configs['data_file'])
    self.sensors: list[dict[str, str]] = configs['sensors']
    self.create_data_file()
    self.update_interval: int = configs['update_interval']
    self.test_mode = self.name == 'test'

  def create_data_file(self):
    """Create data file if none exists and write column headers."""
    headers = [s['name'] for s in self.sensors]
    headers = 'time,' + ','.join(headers) + '\n'
    if not os.path.exists(self.data_file):
      with open(self.data_file, 'w') as f:
        f.write(headers)

  def read_sensors(self):
    """Read sensor values."""
    if self.test_mode:
      return [random.randint(0, 1023) for _ in self.sensors]
    raise NotImplementedError

  def write_data(self):
    """Create a data file if none exists and append data to end."""
    time = datetime.now().strftime(DATE_FORMAT)
    values = self.read_sensors()
    row = time + ',' + ','.join(str(v) for v in values) + '\n'
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
